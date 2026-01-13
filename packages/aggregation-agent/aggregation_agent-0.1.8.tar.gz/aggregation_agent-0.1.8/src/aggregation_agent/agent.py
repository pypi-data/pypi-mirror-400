"""
Aggregation Agent - Suggests and implements data aggregation strategies.
"""

import datetime
import json
import logging
import re
import traceback
from copy import deepcopy
from types import SimpleNamespace
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import tiktoken
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
    is_string_dtype,
)
from sfn_blueprint import SFNAgent, SFNAIHandler, SFNDataLoader

from .config import (
    BOOLEAN_DATA_TYPES,
    DATETIME_DATA_TYPES,
    DEFAULT_BOOLEAN_AGGREGATIONS,
    DEFAULT_DATETIME_AGGREGATIONS,
    DEFAULT_NUMERIC_AGGREGATIONS,
    DEFAULT_TEXT_AGGREGATIONS,
    NUMERICAL_DATA_TYPES,
    AggregationConfig,
)
from .constants import (
    format_golden_wizard_aggregation_suggestion_prompt,
    format_group_by_columns_prompt_golden_wizard,
    format_other_wizard_aggregation_suggestion_prompt,
    format_other_wizard_group_by_columns,
)

logger = logging.getLogger(__name__)


class AggregationAgent(SFNAgent):
    """
    Agent for suggesting optimal aggregation methods for features.

    This agent analyzes table schema and field mappings to suggest
    appropriate aggregation methods for each feature when grouping data.
    """

    def __init__(self, config: Optional[AggregationConfig] = None):
        """
        Initialize the Aggregation Agent.

        Args:
            model_name: Name of the model to use
        """
        super().__init__(name="Aggregation Advisor", role="Data Aggregation Advisor")
        self.config = config or AggregationConfig()
        self.ai_handler = SFNAIHandler()
        self.data_loader = SFNDataLoader()
        self.token = tiktoken.encoding_for_model("gpt-4o-mini")

        # Define allowed aggregation methods per data type
        self.allowed_methods = {
            "TEXT": ["Unique Count", "Mode", "Last Value"],
            "NUMERICAL": ["Min", "Max", "Sum", "Mean", "Median", "Mode", "Last Value"],
            "DATETIME": ["Max", "Min"],
            "BOOLEAN": ["Mode", "Last Value"],
        }

    def _get_dataframe_metadata(self, df: pd.DataFrame) -> Dict[str, Any]:
        df = df.convert_dtypes()

        meta_data = {"table_info": {"row_count": len(df)}, "table_columns_info": {}}

        for col in df.columns:
            col_info = {}
            col_series = df[col]

            col_info["data_type"] = str(col_series.dtype)

            null_percentage = float(col_series.isnull().sum() / len(df) * 100)
            col_info["null_percentage"] = round(null_percentage, 2)

            if null_percentage >= 99:
                col_info["distinct_count"] = 0
                col_info["freq/top5"] = []
                col_info["min/max_value"] = []
                col_info["date_distribution"] = []
            else:
                try:
                    distinct_count = int(col_series.nunique())
                except TypeError:
                    distinct_count = int(col_series.astype(str).nunique())
                col_info["distinct_count"] = distinct_count

                try:
                    freq_top5 = list(col_series.value_counts().head(5).items())
                except TypeError:
                    freq_top5 = list(
                        col_series.astype(str).value_counts().head(5).items()
                    )
                col_info["freq/top5"] = freq_top5

                try:
                    min_val, max_val = col_series.min(), col_series.max()
                    col_info["min/max_value"] = [(min_val, max_val)]
                except:  # noqa: E722
                    col_info["min/max_value"] = []

                date_distribution = []
                if (
                    col_series.dtype == "object"
                    or "datetime" in str(col_series.dtype).lower()
                ):
                    try:
                        date_series = pd.to_datetime(
                            col_series, errors="coerce", format="%Y-%m-%d"
                        )
                        valid_dates = date_series.dropna()

                        if len(valid_dates) > 0:
                            date_counts = (
                                valid_dates.dt.date.value_counts().sort_index()
                            )
                            date_distribution = [
                                (date, count) for date, count in date_counts.items()
                            ]
                    except:  # noqa: E722
                        pass

                col_info["date_distribution"] = date_distribution

            meta_data["table_columns_info"][col] = col_info

        return meta_data

    def _get_group_by_field(
        self,
        business_domain: str,
        business_domain_description: str,
        column_descriptions: dict,
        entity_description: dict,
        mappings: dict,
        table_category,
        df=None,
        sample_data=None,
        metadata=None,
        use_case=None,
    ):
        logger.info("Sending group by method suggestion prompt to LLM")

        try:
            if isinstance(df, pd.DataFrame) and not df.empty:
                meta_data = self._get_dataframe_metadata(df)
                meta_data = json.dumps(meta_data, indent=4, default=str)

                # Clean and sample data
                clean_df = df.dropna()
                sample_size = min(len(clean_df), 7)
                if sample_size > 0:
                    sample = clean_df.sample(n=sample_size, random_state=42)
                    sample_json = sample.to_json(
                        orient="records", indent=4, date_format="iso"
                    )
                else:
                    sample_json = "[]"
                    logger.warning("No data available after cleaning DataFrame")
            else:
                meta_data = metadata
                sample_json = sample_data

            # Build business domain context
            business_domain_context = (
                f"{business_domain} : {business_domain_description}"
            )

            column_text = json.dumps(column_descriptions, indent=4)
            entity_text = json.dumps(entity_description, indent=4)
            mappings_text = json.dumps(mappings, indent=4)

            if use_case:
                system_prompt, user_prompt = format_other_wizard_group_by_columns(
                    use_case=use_case,
                    business_domain=business_domain_context,
                    entity_description=entity_text,
                    column_descriptions=column_text,
                    sample_data=sample_json,
                    meta_data=meta_data,
                    mappings=mappings_text,
                )
            else:
                system_prompt, user_prompt = (
                    format_group_by_columns_prompt_golden_wizard(
                        sample_data=sample_json,
                        meta_data=meta_data,
                        mappings=mappings_text,
                        business_domain=business_domain_context,
                        table_category=table_category,
                        entity_description=entity_text,
                    )
                )

            response, cost = self.ai_handler.route_to(
                self.config.group_by_ai_provider,
                configuration={
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "max_tokens": self.config.max_tokens,
                    "temperature": self.config.temperature,
                },
                model=self.config.group_by_model,
            )

            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]  # Remove ```json
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            
            return json.loads(clean_response), cost
        except Exception as e:
            logger.error(f"Error in LLM suggestion phase: {str(e)}")
            return []

    def _clean_json_string(self, json_string, data_df, dtype_dict):
        logger.info("cleaning json string...")

        json_match = re.search(
            r"```(?:json)?\s*(\{.*?\})\s*```", json_string, re.DOTALL
        )

        if json_match:
            json_string = json_match.group(1)
        else:
            json_match = re.search(r"^\s*(\{.*\})\s*$", json_string, re.DOTALL)
            if json_match:
                json_string = json_match.group(1)
            else:
                json_string = json_string.strip()

        # Strip leading and trailing whitespace
        json_string = json_string.strip()

        if json_string.startswith("```json"):
            json_string = json_string[7:-3]

        # Check if the cleaned string represents a valid JSON dictionary
        try:
            cleaned_dict = json.loads(json_string)
            if not isinstance(cleaned_dict, dict):
                raise ValueError("Not a valid JSON dictionary")
        except (ValueError, json.decoder.JSONDecodeError):
            raise ValueError("Not a valid JSON dictionary")

        # Check if there are any keys in the cleaned dictionary
        if len(cleaned_dict) == 0:
            logger.info(" Cleaned JSON is empty..")
        else:
            logger.info(
                f" Number of columns present in cleaned JSON are {len(cleaned_dict)}"
            )

        # Check if keys are present in DataFrame columns
        missing_columns = []
        for key in cleaned_dict.keys():
            if key not in data_df.columns:
                missing_columns.append(key)

        if missing_columns:
            logger.info(
                " Warning: The following keys from the cleaned JSON dictionary are not present as columns in the DataFrame:"
            )
            logger.info(f" {missing_columns}'")
        else:
            logger.info("All columns identified.")

        for column, methods in list(cleaned_dict.items()):
            if isinstance(methods, list):
                data_type = dtype_dict.get(column)

                if data_type in self.allowed_methods:
                    allowed_methods = self.allowed_methods[data_type]

                    valid_methods = [
                        method
                        for method in methods
                        if method["method"] in allowed_methods
                    ]

                    if valid_methods:
                        if len(valid_methods) != len(methods):
                            logger.info(
                                f"Invalid methods removed for column '{column}': {[method['method'] for method in methods if method['method'] not in allowed_methods]}"
                            )

                        cleaned_dict[column] = valid_methods
                    else:
                        logger.info(
                            f"No valid methods for column '{column}', removing column"
                        )
                        del cleaned_dict[column]
                else:
                    logger.info(
                        f"Data type '{data_type}' is not allowed, removing column '{column}'"
                    )
                    del cleaned_dict[column]
            else:
                logger.info(
                    f"Methods for column '{column}' are not a list, removing column"
                )

                del cleaned_dict[column]

        return cleaned_dict if cleaned_dict else None

    def format_response(self, cleaned_json, op_col_dtypes):
        data = dict()

        for op_cod in op_col_dtypes:
            op_col, op_dtype = op_cod["column_name"], op_cod["data_type"]

            op_dtype = op_dtype.lower() if op_dtype else None
            if op_dtype in NUMERICAL_DATA_TYPES:
                curr_agg = deepcopy(DEFAULT_NUMERIC_AGGREGATIONS)
            elif op_dtype in DATETIME_DATA_TYPES:
                curr_agg = deepcopy(DEFAULT_DATETIME_AGGREGATIONS)
            elif op_dtype in BOOLEAN_DATA_TYPES:
                curr_agg = deepcopy(DEFAULT_BOOLEAN_AGGREGATIONS)
            else:
                curr_agg = deepcopy(DEFAULT_TEXT_AGGREGATIONS)
            agg_sugg = cleaned_json.get(op_col.lower(), [])

            for agg in agg_sugg:
                cagg = agg.get("method").lower().replace(" ", "_")
                curr_agg[cagg]["checked"] = True
                curr_agg[cagg]["explanation"] = agg.get("explanation")

            # Add missing explanations as empty strings
            for agg_detail in curr_agg.values():
                if "explanation" not in agg_detail:
                    agg_detail["explanation"] = ""

            obj = {
                "datatype": op_dtype,
                "aggregations": list(curr_agg.values()),
            }

            data[op_col] = obj
        return data


    def suggest_aggregation_methods(
        self,
        data_df,
        column_text_describe_dict,
        group_by_columnes,
        feature_dtype_dict,
        use_case=None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Suggest aggregation methods for features based on their data types and the problem context.
        """
        logger.info("Suggesting aggregation methods")

        try:
            df_columns = [col.lower() for col in data_df.columns]
            group_by_columns = [col.lower() for col in group_by_columnes]

            for col in column_text_describe_dict.keys():
                if col.lower() not in df_columns:
                    logger.info(
                        f"Key '{col}' in column_text_describe_dict but not found as a column in data_df."
                    )

            for col in group_by_columns:
                if col.lower() not in df_columns:
                    raise ValueError(f"Group by column '{col}' not found in data_df.")

            if len(data_df) == len(data_df.groupby(group_by_columnes)):
                logger.info(
                    "Only one record per group. Returning appropriate aggregation for all features."
                )

                default_methods = {
                    "TEXT": {
                        "method": "Last Value",
                        "explanation": "With only one record per group, Last Value returns the single available value.",
                    },
                    "NUMERICAL": {
                        "method": "Sum",
                        "explanation": "With only one record per group, Sum returns the single available value.",
                    },
                    "DATETIME": {
                        "method": "Max",
                        "explanation": "With only one record per group, max returns the single available value.",
                    },
                    "BOOLEAN": {
                        "method": "Mode",
                        "explanation": "With only one record per group, mode returns the single available value.",
                    },
                }

                aggregation_suggestion = {}

                for col in data_df.columns:
                    if col in group_by_columns:
                        continue

                    dtype = feature_dtype_dict.get(col)

                    if dtype in default_methods:
                        aggregation_suggestion[col] = [default_methods[dtype]]
                    else:
                        logger.info(
                            f"Warning: Data type for column '{col}' not recognized, skipping."
                        )

                return aggregation_suggestion, {}

            clean_df = data_df.dropna()
            sample = clean_df.sample(n=min(len(clean_df), 10), random_state=42)
            sample_json = sample.to_json(orient="records", indent=4, date_format="iso")

            df_describe_dict = data_df.describe().to_json(
                orient="records", indent=4, date_format="iso"
            )

            total_token = (
                len(self.token.encode(str(sample_json)))
                + len(self.token.encode(str(df_describe_dict)))
                + len(self.token.encode(str(column_text_describe_dict)))
                + len(self.token.encode(str(feature_dtype_dict)))
            )

            if total_token > 11000:
                removed_cols = data_df.columns[-25:]
                data_df = data_df.iloc[:, :-25]

                for col in removed_cols:
                    if col in column_text_describe_dict:
                        logger.info(
                            f"removing the respective {col} from the describe dict."
                        )

                        del column_text_describe_dict[col]
                    if col in feature_dtype_dict:
                        logger.info(
                            f"removing the respective {col} from the dtype dict."
                        )

                        del feature_dtype_dict[col]

                sample = clean_df.sample(n=min(len(clean_df), 5), random_state=42)

                sample_json = sample.to_json(
                    orient="records", indent=4, date_format="iso"
                )

                df_describe_dict = data_df.describe().to_json(
                    orient="records", indent=4, date_format="iso"
                )

            if use_case:
                system_prompt, user_prompt = (
                    format_other_wizard_aggregation_suggestion_prompt(
                        group_by_columns=group_by_columns,
                        use_case=use_case,
                        feature_dtype_dict=json.dumps(feature_dtype_dict, indent=4),
                        column_text_describe_dict=json.dumps(
                            column_text_describe_dict, indent=4
                        ),
                        df_describe_dict=df_describe_dict,
                        sample_data_dict=sample_json,
                    )
                )
            else:
                system_prompt, user_prompt = (
                    format_golden_wizard_aggregation_suggestion_prompt(
                        feature_dtype_dict=json.dumps(feature_dtype_dict, indent=4),
                        df_describe_dict=df_describe_dict,
                        sample_data_dict=sample_json,
                        column_text_describe_dict=json.dumps(
                            column_text_describe_dict, indent=4
                        ),
                    )
                )

            cost_summary = {}

            for _ in range(3):
                response, cost = self.ai_handler.route_to(
                    self.config.aggregation_ai_provider,
                    configuration={
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "max_tokens": self.config.max_tokens,
                        "temperature": self.config.temperature,
                    },
                    model=self.config.aggregation_model,
                )

                cost_summary = {
                    k: cost.get(k, 0) + cost_summary.get(k, 0)
                    for k in set(cost) | set(cost_summary)
                }

                generated_texts = response.strip()

                cleaned_json = self._clean_json_string(
                    generated_texts, data_df, feature_dtype_dict
                )

                logger.info(
                    "Successfully parsed aggregation method suggestions from LLM response"
                )

                if cleaned_json and len(cleaned_json) > 4:
                    all_same = (
                        len(
                            set(
                                tuple(tuple(d.items()) for d in v)
                                for v in cleaned_json.values()
                            )
                        )
                        == 1
                    )

                    if not all_same:
                        return cleaned_json, cost_summary
                    else:
                        logger.warning(
                            "All suggested aggregation methods are the same. Trying again."
                        )
                elif cleaned_json and len(cleaned_json) <= 4:
                    logger.info(
                        "Output has fewer than 5 features. Returning the output."
                    )
                    return cleaned_json, cost_summary
                else:
                    logger.warning("Output does not meet the criteria. Trying again.")

            logger.warning(
                "Output check limit reached 3 iterations. Returning the last output."
            )

            return cleaned_json, cost_summary
        except Exception as e:
            logger.error(f"Error in LLM suggestion phase: {str(e)}")
            logger.error(f"\n\n\nTRACEBACK: {traceback.format_exc()}")
            return {}, {}

    def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an aggregation task based on the provided task data.
        This method provides a standard interface for the orchestrator.

        Args:
            task_data: Dictionary containing task information
                - file: File path or data source
                - problem_context: Context about the aggregation task
                - domain_schema: Optional domain schema path

        Returns:
            Dictionary with execution results
        """


        try:
            data_source = task_data["file"]
            domain_name = task_data["domain_name"]
            domain_description = task_data["domain_description"]
            column_describe: dict = task_data["column_description"]
            entity_description: dict = task_data["entity_description"]
            mappings: dict = task_data["mappings"]
            table_category = task_data["table_category"]
            use_case = task_data.get("use_case")
            feature_dtype = task_data.get("feature_dtype")

            df = self.data_loader.execute_task(SimpleNamespace(path=data_source))

            group_by_columns, cost_summary_group = self._get_group_by_field(
                df=df,
                business_domain=domain_name,
                business_domain_description=domain_description,
                column_descriptions=column_describe,
                entity_description=entity_description,
                mappings=mappings,
                use_case=use_case,
                table_category=table_category,
            )

            if not group_by_columns:
                logger.error("No group by column suggested by LLM.")
                raise ValueError("No valid group by column found.")
            # print("Group by columns: ", group_by_columns)
            aggregation_suggestion, cost_summary_aggregation = (
                self.suggest_aggregation_methods(
                    df,
                    column_text_describe_dict=column_describe,
                    group_by_columnes=group_by_columns,
                    use_case=use_case,
                    feature_dtype_dict=feature_dtype,
                )
            )

            if not aggregation_suggestion:
                logger.error("No aggregation suggestions generated by LLM.")
                raise RuntimeError("Failed to get aggregation suggestions from LLM.")

            if "workflow_storage_path" in task_data or "workflow_id" in task_data:
                try:
                    from sfn_blueprint import WorkflowStorageManager

                    storage_manager = WorkflowStorageManager(
                        task_data.get("workflow_storage_path", "outputs/workflows"),
                        task_data.get("workflow_id", "unknown"),
                    )
                    storage_result = storage_manager.save_agent_result(
                        agent_name=self.__class__.__name__,
                        step_name="aggregation_suggestion",
                        data={
                            "aggregation_suggestions": aggregation_suggestion,
                            "groupby_columns": group_by_columns,
                            "cost_summary_group": cost_summary_group,
                            "cost_summary_aggregation": cost_summary_aggregation,
                        },
                        metadata={
                            "domain_name": domain_name,
                            "domain_description": domain_description,
                            "column_text_describe_dict": column_describe,
                            "group_by_columns": group_by_columns,
                            "entity_description": entity_description,
                            "mappings": mappings,
                            "use_case": use_case,
                        },
                    )
                    logger.info(
                        f"Aggregation suggestions saved to workflow storage: {storage_result.get('files')}"
                    )
                except ImportError:
                    logger.warning("WorkflowStorageManager not available, skipping.")
                except Exception as e:
                    logger.warning(f"Failed to save to workflow storage: {e}")

            return {
                "success": True,
                "result": {
                    "aggregation_suggestions": aggregation_suggestion,
                    "groupby_columns": group_by_columns,
                    "cost_summary_group": cost_summary_group,
                    "cost_summary_aggregation": cost_summary_aggregation,
                    "message": "Aggregation methods suggested and validated successfully.",
                },
                "agent": self.__class__.__name__,
            }
        except Exception as e:
            logger.error(f"Task execution failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Task execution failed: {str(e)}",
                "agent": self.__class__.__name__,
            }

    def __call__(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.execute_task(task_data)
