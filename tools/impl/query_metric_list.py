from tools.tool import BaseTool


class QueryMetricList(BaseTool):
    def __init__(self):
        super().__init__(name="query_metric_list",
                         description="查询当前平台的指标列表",
                         parameters={})

    def execute(self) -> dict:
        return {
            "data": [{"metric_code": "1322",
                      "display_name": "近七天茅台销售总额"},
                     {"metric_code": "12",
                      "display_name": "昨日茅台销售总额"}],
            "description": "当前租户所有的指标"
        }
