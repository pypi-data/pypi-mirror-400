"""
HSR 云雨平台数据获取 MCP 工具
功能：调用 Dify 工作流获取 CVM 性能报告数据，计算差距百分比，生成 Markdown 表格

MCP 工具说明：
- 工具名称: compare_cvm_reports
- 用途: 对比两个机型的 CVM 性能测试报告，自动计算各指标的百分比差异
- 输入: 两个机型的报告 ID 列表，Dify API 密钥，可选的输出文件路径
- 输出: 包含百分比差异列的 Markdown 格式表格
"""

import logging
from typing import Optional
from mcp.server.fastmcp import FastMCP
import requests

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 MCP 服务器实例
mcp = FastMCP("hsr-getyundata")


class ReportCompare:
    """报告对比类"""
    
    BASE_URL = "http://idify.woa.com/v1"
    
    def __init__(self, api_key: str):
        """
        初始化
        :param api_key: Dify API 密钥
        """
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def run_workflow(self, inputs: dict) -> dict:
        """
        运行 Dify 工作流
        :param inputs: 工作流输入参数
        :return: 包含 'result' 的字典
        """
        url = f"{self.BASE_URL}/workflows/run"
        payload = {
            "inputs": inputs,
            "response_mode": "blocking",
            "user": "mcp-tool"
        }
        
        try:
            logger.info(f"Running workflow with inputs: {inputs}")
            response = requests.post(url, headers=self.headers, json=payload, timeout=1000)
            
            if response.status_code != 200:
                logger.error(f"Dify API Error: {response.status_code} - {response.text}")
                return {'result': f"Workflow Error ({response.status_code}): {response.text}"}
            
            result = response.json()
            outputs = result.get('data', {}).get('outputs', {})
            return {'result': outputs.get('result', str(outputs))}
            
        except Exception as e:
            logger.error(f"Error running workflow: {str(e)}")
            return {'result': f"工作流执行失败: {str(e)}"}
    
    def merge_report_ids(self, ids_a: str, ids_b: str) -> str:
        """
        合并两个机型的报告 ID，交替排列
        :param ids_a: 机型 A 的报告 ID 字符串，如 "1,2,3"
        :param ids_b: 机型 B 的报告 ID 字符串，如 "4,5,6"
        :return: 合并后的字符串，如 "1,4,2,5,3,6"
        """
        list_a = [x.strip() for x in ids_a.split(',') if x.strip()]
        list_b = [x.strip() for x in ids_b.split(',') if x.strip()]
        
        if len(list_a) != len(list_b):
            raise ValueError(f"两个机型的报告数量不一致: A={len(list_a)}, B={len(list_b)}")
        
        merged = []
        for a, b in zip(list_a, list_b):
            merged.append(a)
            merged.append(b)
        
        return ','.join(merged)
    
    def parse_markdown_table(self, md_content: str) -> tuple:
        """
        解析 Markdown 表格
        :param md_content: Markdown 表格字符串
        :return: (headers, rows) 元组
        """
        lines = md_content.strip().split('\n')
        if len(lines) < 2:
            raise ValueError("无效的 Markdown 表格格式")
        
        # 解析表头
        header_line = lines[0]
        headers = [h.strip() for h in header_line.split('|') if h.strip()]
        
        # 跳过分隔行，解析数据行
        rows = []
        for line in lines[2:]:
            if line.strip():
                cells = [c.strip() for c in line.split('|') if c.strip()]
                if cells:
                    rows.append(cells)
        
        return headers, rows
    
    def calculate_percentage_diff(self, val_a: str, val_b: str) -> str:
        """
        计算百分比差异: (val_b - val_a) / val_a * 100
        :param val_a: 基准值（机型 A）
        :param val_b: 对比值（机型 B）
        :return: 百分比字符串，如 "+5.2%" 或 "-3.1%"
        """
        try:
            if val_a == "N/A" or val_b == "N/A":
                return "N/A"
            
            a = float(val_a)
            b = float(val_b)
            
            if a == 0:
                if b == 0:
                    return "0.0%"
                return "N/A"
            
            diff_pct = ((b - a) / abs(a)) * 100
            sign = "+" if diff_pct > 0 else ""
            return f"{sign}{diff_pct:.2f}%"
        except (ValueError, TypeError):
            return "N/A"
    
    def insert_percentage_columns(self, md_content: str) -> str:
        """
        在 Markdown 表格中每隔两列插入百分比差异列
        :param md_content: 原始 Markdown 表格
        :return: 插入百分比列后的 Markdown 表格
        """
        headers, rows = self.parse_markdown_table(md_content)
        
        # 前 3 列是固定的: test_name, metric, metric_unit
        fixed_cols = 3
        data_headers = headers[fixed_cols:]  # Report 列
        
        if len(data_headers) < 2:
            logger.warning("数据列少于 2 列，无法计算百分比")
            return md_content
        
        # 构建新表头
        new_headers = headers[:fixed_cols]
        for i in range(0, len(data_headers), 2):
            new_headers.append(data_headers[i])  # 机型 A
            if i + 1 < len(data_headers):
                new_headers.append(data_headers[i + 1])  # 机型 B
                # 提取报告 ID 用于命名
                report_a = data_headers[i].replace("Report ", "")
                report_b = data_headers[i + 1].replace("Report ", "")
                new_headers.append(f"差异% ({report_b} vs {report_a})")
        
        # 构建新数据行
        new_rows = []
        for row in rows:
            if len(row) < fixed_cols:
                continue
            
            new_row = row[:fixed_cols]
            data_cells = row[fixed_cols:]
            
            for i in range(0, len(data_cells), 2):
                new_row.append(data_cells[i] if i < len(data_cells) else "N/A")
                if i + 1 < len(data_cells):
                    new_row.append(data_cells[i + 1])
                    # 计算百分比差异
                    pct = self.calculate_percentage_diff(data_cells[i], data_cells[i + 1])
                    new_row.append(pct)
            
            new_rows.append(new_row)
        
        # 生成新的 Markdown 表格
        header_line = "| " + " | ".join(new_headers) + " |"
        separator = "|" + "---|" * len(new_headers)
        
        row_lines = []
        for row in new_rows:
            row_lines.append("| " + " | ".join(row) + " |")
        
        return "\n".join([header_line, separator] + row_lines)
    
    def compare_reports(
        self,
        ids_a: str,
        ids_b: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        对比两个机型的报告
        :param ids_a: 机型 A 的报告 ID 字符串
        :param ids_b: 机型 B 的报告 ID 字符串
        :param output_path: 输出文件路径（可选）
        :return: 带百分比差异的 Markdown 表格字符串
        """
        # 1. 合并报告 ID
        merged_ids = self.merge_report_ids(ids_a, ids_b)
        logger.info(f"合并后的报告 ID: {merged_ids}")
        
        # 2. 调用 Dify 工作流
        inputs = {"report_ids": merged_ids}
        
        workflow_result = self.run_workflow(inputs)
        md_content = workflow_result.get('result', '')
        
        if not md_content or md_content.startswith("Workflow Error") or md_content.startswith("工作流执行失败"):
            logger.error(f"工作流返回错误: {md_content}")
            return md_content
        
        logger.info("工作流返回成功，开始处理数据")
        
        # 3. 插入百分比差异列
        result_md = self.insert_percentage_columns(md_content)
        
        # 4. 保存到文件（如果指定了路径）
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result_md)
                logger.info(f"报告已保存到: {output_path}")
            except Exception as e:
                logger.error(f"保存文件失败: {str(e)}")
        
        return result_md


@mcp.tool()
def compare_cvm_reports(
    ids_a: str,
    ids_b: str,
    api_key: str,
    output_path: str = ""
) -> str:
    """
    对比两个机型的 CVM 性能测试报告，自动计算各指标的百分比差异。
    
    该工具用于从云雨平台获取 CVM 性能测试数据，并生成包含对比分析的 Markdown 表格。
    工具会自动将两个机型的报告 ID 交替合并，调用 Dify 工作流获取原始数据，
    然后在每两列数据后插入百分比差异列，便于直观对比两个机型的性能差异。
    
    使用场景：
    - 对比不同机型的 CVM 性能测试结果
    - 分析新旧版本机型的性能变化
    - 生成性能对比报告文档
    
    参数说明：
    - ids_a: 机型 A（基准机型）的报告 ID 列表，多个 ID 用英文逗号分隔。
             例如: "10000011205,10000011206,10000011207"
             这些 ID 来自云雨平台的测试报告，每个 ID 对应一次测试运行的结果。
             
    - ids_b: 机型 B（对比机型）的报告 ID 列表，多个 ID 用英文逗号分隔。
             例如: "10000008638,10000008532,10000008536"
             注意：ids_b 的报告数量必须与 ids_a 相同，且顺序对应。
             
    - api_key: Dify 工作流的 API 密钥，用于调用云雨数据获取工作流。
               格式通常为 "app-xxxxxxxxxxxxxxxxxxxxxxxx"
               
    - output_path: (可选) 输出 Markdown 文件的绝对路径。
                   如果提供，结果将同时保存到该文件。
                   例如: "/data/workspace/reports/compare_result.md"
                   如果不提供或为空字符串，则只返回结果不保存文件。
                   
                   **重要**: 只有当用户明确要求保存文件时才指定此参数。
                   如果用户提示词中没有要求保存文件或指定输出路径，请勿传递此参数。
    
    返回值：
    - 成功时返回 Markdown 格式的表格字符串，包含以下列：
      * test_name: 测试名称（如 alexnet_baseline, lmbench_baseline）
      * metric: 指标名称（如 #forward across 100 steps, #L1延时）
      * metric_unit: 指标单位说明
      * Report {id_a}: 机型 A 的测试值
      * Report {id_b}: 机型 B 的测试值
      * 差异% ({id_b} vs {id_a}): 百分比差异，正值表示 B 比 A 大，负值表示 B 比 A 小
      
    - 失败时返回错误信息字符串，以 "Workflow Error" 或 "工作流执行失败" 开头
    
    示例调用：
    ```
    result = compare_cvm_reports(
        ids_a="10000011205,10000011206",
        ids_b="10000008638,10000008532",
        api_key="app-fdIjbKi5xMQytXMtr91C6FtA",
        output_path="/data/workspace/report.md"
    )
    ```
    
    输出示例：
    ```
    | test_name | metric | metric_unit | Report 10000011205 | Report 10000008638 | 差异% (10000008638 vs 10000011205) |
    |---|---|---|---|---|---|
    | alexnet_baseline | #forward across 100 steps | #forward across 100 steps(单位: ms) | 153.0 | 145.0 | -5.23% |
    | lmbench_baseline | #L1延时 | #L1延时(单位: ns) | 0.889 | 0.912 | +2.59% |
    ```
    
    注意事项：
    1. 两个机型的报告 ID 数量必须相同
    2. 报告 ID 的顺序应该对应（第一个 A 对比第一个 B，以此类推）
    3. API 密钥需要有访问 Dify 工作流的权限
    4. 如果某个指标值为 null 或无法计算，差异列将显示 "N/A"
    
    Args:
        ids_a: 机型 A 的报告 ID 字符串，多个 ID 用逗号分隔
        ids_b: 机型 B 的报告 ID 字符串，多个 ID 用逗号分隔
        api_key: Dify 工作流 API 密钥
        output_path: 输出文件路径（可选，默认为空不保存文件）
    
    Returns:
        Markdown 格式的对比表格字符串，包含百分比差异列
    """
    try:
        comparer = ReportCompare(api_key=api_key)
        result = comparer.compare_reports(
            ids_a=ids_a,
            ids_b=ids_b,
            output_path=output_path if output_path else None
        )
        return result
    except ValueError as e:
        return f"参数错误: {str(e)}"
    except Exception as e:
        logger.error(f"工具执行失败: {str(e)}")
        return f"执行失败: {str(e)}"


@mcp.tool()
def get_single_report(
    report_ids: str,
    api_key: str,
    output_path: str = ""
) -> str:
    """
    获取单个或多个报告的原始数据（不进行对比计算）。
    
    该工具用于从云雨平台获取 CVM 性能测试报告的原始数据，返回 Markdown 表格格式。
    与 compare_cvm_reports 不同，此工具不会计算百分比差异，适用于查看单个机型的测试结果。
    
    使用场景：
    - 查看单个机型的性能测试详情
    - 获取多个报告的原始数据用于自定义分析
    - 导出测试报告数据
    
    参数说明：
    - report_ids: 报告 ID 列表，多个 ID 用英文逗号分隔。
                  例如: "10000011205,10000011206,10000011207"
                  
    - api_key: Dify 工作流的 API 密钥
    
    - output_path: (可选) 输出 Markdown 文件的绝对路径。
                   如果提供，结果将同时保存到该文件。
                   例如: "/data/workspace/reports/compare_result.md"
                   如果不提供或为空字符串，则只返回结果不保存文件。
                   
                   **重要**: 只有当用户明确要求保存文件时才指定此参数。
                   如果用户提示词中没有要求保存文件或指定输出路径，请勿传递此参数。
    
    返回值：
    - Markdown 格式的表格字符串，包含所有报告的测试数据
    
    Args:
        report_ids: 报告 ID 字符串，多个 ID 用逗号分隔
        api_key: Dify 工作流 API 密钥
        output_path: 输出文件路径（可选）
    
    Returns:
        Markdown 格式的报告数据表格
    """
    try:
        comparer = ReportCompare(api_key=api_key)
        inputs = {"report_ids": report_ids}
        
        workflow_result = comparer.run_workflow(inputs)
        md_content = workflow_result.get('result', '')
        
        if not md_content or md_content.startswith("Workflow Error") or md_content.startswith("工作流执行失败"):
            return md_content
        
        # 保存到文件（如果指定了路径）
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                logger.info(f"报告已保存到: {output_path}")
            except Exception as e:
                logger.error(f"保存文件失败: {str(e)}")
        
        return md_content
        
    except Exception as e:
        logger.error(f"工具执行失败: {str(e)}")
        return f"执行失败: {str(e)}"


# 主入口
def main() -> None:
    # 启动 MCP 服务器
    mcp.run(transport="stdio")
