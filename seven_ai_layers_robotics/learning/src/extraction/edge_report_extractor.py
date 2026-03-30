# -*- coding: utf-8 -*-
"""
Edge Report 数据清洗与去重提取器
负责从数据库导出数据，进行异常值过滤和去重处理，并回写到数据库
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from sqlalchemy import create_engine, text


class EdgeReportExtractor:
    """Edge Report 数据提取器 - 处理数据清洗、去重和回写"""

    def __init__(self, db_config: Dict[str, Any]):
        """
        初始化提取器
        :param db_config: 数据库配置字典
        """
        self.db_config = db_config
        self.db_uri = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}?charset=utf8mb4"

        # 参数列（业务唯一配方 + 工艺）
        self.param_cols = [
            "Formula PVK", "Concentration PVK",
            "Formula Additive 1", "Concentration Additive 1",
            "Formula Additive 2", "Concentration Additive 2",
            "Formula Additive 3", "Concentration Additive 3",
            "Formula SAM 1", "Concentration SAM 1",
            "Formula SAM 2", "Concentration SAM 2",
            "Formula SAM 3", "Concentration SAM 3",
            "Spin Coating Speed SAM", "Spin Coating Time SAM",
            "Annealed Temperature SAM", "Annealed Time SAM",
            "Spin Coating Speed PVK 1", "Spin Coating Time PVK 1",
            "Spin Coating Speed PVK 2", "Spin Coating Time PVK 2",
            "Antisolvent Dropping Timing", "Antisolvent Volume",
            "Annealed Temperature PVK", "Annealed Time PVK",
            "Formula Passivator 1", "Concentration Passivator 1",
            "Formula Passivator 2", "Concentration Passivator 2",
            "Formula Passivator 3", "Concentration Passivator 3",
            "Formula Passivator 4", "Concentration Passivator 4",
            "Spin Coating Speed Passivator", "Spin Coating Time Passivator",
            "Passivator Dropping Timing", "Passivator Volume",
            "Annealed Temperature Passivator", "Annealed Time Passivator",
        ]

        # 指标列
        self.metric_cols = ["PCE", "FF", "Voc", "Jsc"]

        # 所有写入列
        self.all_write_cols = ["No"] + self.param_cols + self.metric_cols

        # No 分段动态阈值（严格不等号）
        self.no_segments = [
            # (no_lo, no_hi, pce_lo, pce_hi, ff_lo, ff_hi, voc_lo, voc_hi, jsc_lo, jsc_hi)
            (0,     7680,  10, 18,    50, 90,    0.9, 1.15,  15, 24),
            (7681,  32960, 10, 23.5,  50, 90,    0.9, 1.19,  15, 25.5),
            (32961, 42420, 10, 25.56, 50, 90,    0.9, 1.19,  15, 26.5),
            (42421, 50764, 10, 27,    50, 90,    0.9, 1.22,  15, 26.7),
        ]

    def _assert_columns(self, df: pd.DataFrame, required_cols: List[str]) -> None:
        """检查 DataFrame 是否包含所有必需列"""
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise ValueError(f"缺少必要列：{missing}")

    def _coerce_numeric_inplace(self, df: pd.DataFrame) -> None:
        """把 No 与指标列转成数值，无法转的变 NaN"""
        df["No"] = pd.to_numeric(df["No"], errors="coerce")
        for c in self.metric_cols:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    def _filter_by_no_segments(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        按 No 分段的动态去异常规则（向量化实现）
        - No、PCE、FF、Voc、Jsc 必须非空且为可解析数值
        - 再按分段阈值筛选
        """
        self._assert_columns(df, ["No"] + self.metric_cols)

        df = df.copy()
        self._coerce_numeric_inplace(df)

        df = df.dropna(subset=["No"] + self.metric_cols)
        if df.empty:
            return df

        no = df["No"]
        pce, ff, voc, jsc = df["PCE"], df["FF"], df["Voc"], df["Jsc"]

        masks = []
        for (nlo, nhi, p_lo, p_hi, ff_lo, ff_hi, v_lo, v_hi, j_lo, j_hi) in self.no_segments:
            seg = (
                (no >= nlo) & (no <= nhi) &
                (pce > p_lo) & (pce < p_hi) &
                (ff > ff_lo) & (ff < ff_hi) &
                (voc > v_lo) & (voc < v_hi) &
                (jsc > j_lo) & (jsc < j_hi)
            )
            masks.append(seg)

        mask_all = masks[0]
        for m in masks[1:]:
            mask_all = mask_all | m

        return df.loc[mask_all].copy()

    def clean_and_dedup_keep_max_pce(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        1) 去异常（按 No 分段动态阈值）
        2) 去重（按 PARAM_COLS 分组，保留 PCE 最大）
        3) 再去异常一次（防止 idxmax 取到边界外/异常的情况）
        4) 恢复原顺序
        """
        self._assert_columns(df, self.all_write_cols)

        df = df.copy()
        df["_orig_idx"] = range(len(df))

        n0 = len(df)

        # 1) 去异常
        df = self._filter_by_no_segments(df)
        n1 = len(df)
        if df.empty:
            print(f"⚠️ 去异常后为空：{n0} → {n1}")
            return df.drop(columns=["_orig_idx"], errors="ignore")

        # 2) 去重：按列参数分组，保留 PCE 最大
        idx = df.groupby(self.param_cols, dropna=False)["PCE"].idxmax()
        df = df.loc[idx].copy()
        n2 = len(df)

        # 3) 再去异常一次
        df = self._filter_by_no_segments(df)
        n3 = len(df)
        if df.empty:
            print(f"⚠️ 去重后再去异常为空：{n2} → {n3}")
            return df.drop(columns=["_orig_idx"], errors="ignore")

        # 4) 恢复原顺序
        df = df.sort_values("_orig_idx").drop(columns=["_orig_idx"])

        print(f"✅ 清洗统计：原始 {n0} → 去异常 {n1} → 去重 {n2} → 再去异常 {n3}")
        return df

    def export_table_to_csv(self, src_table: str, output_csv: str) -> pd.DataFrame:
        """
        从数据库导出表到 CSV
        :param src_table: 源表名
        :param output_csv: 输出 CSV 路径
        :return: DataFrame
        """
        engine = create_engine(self.db_uri)
        df = pd.read_sql(f"SELECT * FROM `{src_table}`;", con=engine)
        df.to_csv(output_csv, index=False, encoding="utf-8-sig")
        print(f"✅ 已导出 {len(df)} 行 → {output_csv}")
        return df

    def process_csv(self, input_csv: str, output_dir: str) -> pd.DataFrame:
        """
        处理 CSV 文件：清洗 + 去重 → 输出 CSV
        :param input_csv: 输入 CSV 路径
        :param output_dir: 输出目录
        :return: 处理后的 DataFrame
        """
        df = pd.read_csv(input_csv, encoding="utf-8-sig")

        df_out = self.clean_and_dedup_keep_max_pce(df)

        Path(output_dir).mkdir(exist_ok=True)
        out_filename = f"data_clean_dedup_{len(df_out)}rows.csv"
        out_path = Path(output_dir) / out_filename
        df_out.to_csv(out_path, index=False, encoding="utf-8-sig")

        print(f"✅ 清洗完成：{out_path}")
        return df_out

    @staticmethod
    def to_param(col: str) -> str:
        """把 DB / CSV 列名转换为 SQLAlchemy 可用的 bind 参数名"""
        return "p_" + col.replace(" ", "_").replace("-", "_")

    def upsert_to_target_table(self, df: pd.DataFrame, target_table: str) -> None:
        """
        UPSERT 全字段写回目标表
        :param df: 要写入的 DataFrame
        :param target_table: 目标表名
        """
        self._assert_columns(df, self.all_write_cols)

        df_write = df[self.all_write_cols].copy()

        param_map = {col: self.to_param(col) for col in self.all_write_cols}

        insert_cols = ", ".join(f"`{c}`" for c in self.all_write_cols)
        value_cols = ", ".join(f":{param_map[c]}" for c in self.all_write_cols)

        update_cols = ", ".join(
            f"`{c}` = VALUES(`{c}`)" for c in (self.param_cols + self.metric_cols)
        )

        sql = text(f"""
        INSERT INTO `{target_table}` ({insert_cols})
        VALUES ({value_cols})
        ON DUPLICATE KEY UPDATE
            {update_cols}
        """)

        records = []
        for _, row in df_write.iterrows():
            rec = {}
            for col in self.all_write_cols:
                val = row[col]
                if pd.isna(val):
                    val = None
                rec[param_map[col]] = val
            records.append(rec)

        engine = create_engine(self.db_uri)
        with engine.begin() as conn:
            conn.execute(sql, records)

        print(f"✅ 已 UPSERT 全字段写回 {len(records)} 行 → `{target_table}`")

    def extract_and_process(self, src_table: str, target_table: str,
                           output_dir: str = "data") -> bool:
        """
        执行完整的提取、清洗和回写流程
        :param src_table: 源表名
        :param target_table: 目标表名
        :param output_dir: 输出目录（默认 data）
        :return: 成功返回 True，失败抛出 Exception
        """
        try:
            # Step 1: DB → CSV（保存到输出目录）
            Path(output_dir).mkdir(exist_ok=True)
            raw_csv = Path(output_dir) / f"{src_table}_from_db.csv"
            df_raw = self.export_table_to_csv(src_table, str(raw_csv))

            # Step 2: 清洗 + 去重 → 输出 CSV
            df_clean = self.process_csv(raw_csv, output_dir)

            # Step 3: UPSERT 回写
            self.upsert_to_target_table(df_clean, target_table)

            return True

        except Exception as e:
            print(f"❌ 处理失败：{e}")
            raise e
