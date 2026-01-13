import pandas as pd
import numpy as np
import os
import sys
from tqdm import tqdm


class DisruptiveInnovator:
    def __init__(self, net_data="net.csv", time_data="time.csv", focal_data="focal.csv", result_dir="results"):
        """
        初始化计算器。
        """
        # 1. 自动创建结果目录
        self.result_dir = result_dir
        if not os.path.exists(self.result_dir):
            os.makedirs(self.result_dir)
            print(f"Directory created: {self.result_dir}/")

        # 2. 智能加载数据
        self.net_df = self._smart_load(net_data, "net_data")
        self.time_df = self._smart_load(time_data, "time_data")
        self.focal_df = self._smart_load(focal_data, "focal_data")

        # =======================================================
        # [核心修改] 表头适配逻辑：netfrom/netto -> id/cited
        # =======================================================
        # 检查是否包含新版表头
        if 'netfrom' in self.net_df.columns and 'netto' in self.net_df.columns:
            # print(">> [Info] 检测到新版表头 (netfrom, netto)，正在适配为标准格式...")
            self.net_df = self.net_df.rename(columns={'netfrom': 'id', 'netto': 'cited'})

        # 再次检查必要列是否存在，确保数据合规
        if 'id' not in self.net_df.columns or 'cited' not in self.net_df.columns:
            raise ValueError(
                f"net数据列名错误！当前列: {self.net_df.columns.tolist()}\n"
                "程序需要 ['id', 'cited'] 或者 ['netfrom', 'netto']。"
            )
        # =======================================================

        # 3. 数据类型转换
        self.net_df['id'] = self.net_df['id'].astype(str)
        self.net_df['cited'] = self.net_df['cited'].astype(str)

        self.time_df['id'] = self.time_df['id'].astype(str)
        self.time_df["publicationDate"] = pd.to_datetime(self.time_df["publicationDate"])
        self.time_df = self.time_df.drop_duplicates(subset=['id'], keep='first')

        self.focal_df['id'] = self.focal_df['id'].astype(str)
        self.target_ids = self.focal_df['id'].unique().tolist()

        # 4. 构建加速字典
        print("Building dictionaries...")
        # id 是引用者 (netfrom), cited 是被引用者 (netto)
        self.cited_by_dict = self.net_df.groupby('id')['cited'].apply(set).to_dict()
        self.citations_dict = self.net_df.groupby('cited')['id'].apply(set).to_dict()
        self.time_dict = self.time_df.set_index('id')['publicationDate'].to_dict()
        print(f"Preprocessing done. Targets: {len(self.target_ids)}")

    def _smart_load(self, data, name):
        if isinstance(data, str):
            if not os.path.exists(data):
                raise FileNotFoundError(f"File not found: {data}")
            print(f"Loading file: {data}")
            return pd.read_csv(data, low_memory=False)
        elif isinstance(data, pd.DataFrame):
            return data.copy()
        else:
            raise TypeError(f"Invalid type for {name}: {type(data)}")

    def calculate(self, metric_type="DI1", window_years=None, exclude_nk=False):
        """
        计算指标并自动保存到文件。
        """
        valid_metrics = ["DI1", "DI5", "mCD"]
        if metric_type not in valid_metrics:
            raise ValueError(f"Unsupported metric: {metric_type}")

        # 计算窗口天数
        window_days = None
        if window_years == 5:
            window_days = 1825
        elif window_years == 10:
            window_days = 3650
        elif window_years is not None:
            window_days = window_years * 365

        # 生成对应的列名和文件名
        col_name = metric_type
        if exclude_nk: col_name += "nk"
        if window_years: col_name += f"Y{window_years}"

        results = []

        # 使用 sys.stdout 修复进度条串行问题
        for node in tqdm(self.target_ids, desc=f"{col_name:<10}", ncols=100, file=sys.stdout):
            item = {"id": node, col_name: None, "ni": None, "nj": None, "nk": None, "nall": None}
            try:
                citing_nodes_fp_set = self.cited_by_dict.get(node, set())
                cited_nodes_set = self.citations_dict.get(node, set())
                len_cited_by = len(citing_nodes_fp_set)
                len_citations = len(cited_nodes_set)
                date1 = self.time_dict.get(node)

                if len_cited_by > 0 and len_citations > 0:
                    citing_fp_filtered = self._filter_by_time(citing_nodes_fp_set, date1, window_days)
                    citing_fp_filtered_set = set(citing_fp_filtered)

                    citing_sp_temp = set()
                    for s in cited_nodes_set:
                        citing_sp_temp.update(self.cited_by_dict.get(s, set()))
                    if node in citing_sp_temp: citing_sp_temp.remove(node)

                    sp_filtered = self._filter_by_time(citing_sp_temp, date1, window_days)
                    sp_f_set = set(sp_filtered)

                    ni_set = citing_fp_filtered_set - sp_f_set
                    n_i = len(ni_set)
                    nj_set = citing_fp_filtered_set & sp_f_set
                    n_j = len(nj_set)

                    sp_fi_set = cited_nodes_set & sp_f_set
                    n_all_set = citing_fp_filtered_set | sp_f_set
                    if len(sp_fi_set) > 0: n_all_set = n_all_set - sp_fi_set
                    n_all = len(n_all_set)
                    nk_set = n_all_set - citing_fp_filtered_set
                    n_k = len(nk_set)

                    val = None
                    final_nj = n_j
                    if metric_type == "DI1":
                        num = n_i - n_j
                        denom = (n_i + n_j) if exclude_nk else n_all
                        if denom > 0: val = num / denom
                    elif metric_type == "DI5":
                        nj5 = 0
                        if n_j > 0:
                            for i in nj_set:
                                refs_of_i = self.citations_dict.get(i, set())
                                if len(refs_of_i & cited_nodes_set) >= 5: nj5 += 1
                        final_nj = nj5
                        num = n_i - nj5
                        denom = (n_i + nj5) if exclude_nk else n_all
                        if denom > 0: val = num / denom
                    elif metric_type == "mCD":
                        if exclude_nk:
                            val = n_i - n_j
                        else:
                            if n_all > 0: val = (n_i + n_j) * ((n_i - n_j) / n_all)

                    item[col_name] = round(val, 5) if val is not None else None
                    item["ni"] = n_i
                    item["nj"] = final_nj
                    item["nk"] = n_k
                    item["nall"] = n_all

                elif len_cited_by > 0 and len_citations == 0:
                    filtered_cited_by = self._filter_by_time(citing_nodes_fp_set, date1, window_days)
                    n_i_val = len(filtered_cited_by)
                    item[col_name] = 1
                    item["ni"] = n_i_val
                    item["nj"] = 0
                    item["nk"] = 0
                    item["nall"] = n_i_val
                elif len_cited_by == 0 and len_citations > 0:
                    item[col_name] = "f_cited_by_null"
                elif len_cited_by == 0 and len_citations == 0:
                    item[col_name] = "f_cited_by_citation_null"
            except Exception:
                pass
            results.append(item)

        # 结果保存逻辑
        df_result = pd.DataFrame(results)

        # 强制转换为 Int64
        int_cols = ["ni", "nj", "nk", "nall"]
        for col in int_cols:
            if col in df_result.columns:
                df_result[col] = df_result[col].astype("Int64")

        save_path = os.path.join(self.result_dir, f"{col_name}.csv")
        df_result.to_csv(save_path, index=False)

        print(f"Saved to: {save_path}")

        return df_result

    def _filter_by_time(self, nodes_set, base_date, window_days):
        if base_date is pd.NaT or base_date is None: return []
        valid_nodes = []
        for n in nodes_set:
            date2 = self.time_dict.get(n)
            if date2 is not pd.NaT and date2 is not None:
                diff_days = (date2 - base_date).days
                if diff_days > 0:
                    if window_days is None or diff_days < window_days:
                        valid_nodes.append(n)
        return valid_nodes