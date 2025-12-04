import random
import streamlit as st
from datetime import datetime

# ===================== 核心座位逻辑类 =====================
class VisualMeetingSeating:
    def __init__(self, total_people, rows, cols, name_list=None):
        """初始化座位系统"""
        # 基础参数校验
        if rows <= 0 or cols <= 0:
            raise ValueError("行数/列数必须为正整数！")
        if total_people <= 0:
            raise ValueError("参会人数必须为正整数！")
        
        self.total_people = total_people
        self.rows = rows
        self.cols = cols
        # 处理姓名列表（去空、去重）
        self.name_list = []
        if name_list:
            for name in name_list:
                clean_name = name.strip()
                if clean_name and clean_name not in self.name_list:
                    self.name_list.append(clean_name)
        # 补充默认姓名（若列表为空或数量不足）
        if len(self.name_list) < self.total_people:
            default_names = [f"参会人{i+1}" for i in range(self.total_people)]
            self.name_list = self.name_list[:self.total_people] + default_names[len(self.name_list):self.total_people]
        
        # 生成座位表和可视化表
        self.seating_plan = self._create_seating_plan()
        self.visual_plan = self._create_visual_plan()
        
        # 最终校验：确保两个表结构一致
        if len(self.visual_plan) != rows or any(len(row) != cols for row in self.visual_plan):
            raise ValueError("可视化座位表行列数与配置不符！")

    def _create_seating_plan(self):
        """生成随机座位表（姓名映射）"""
        total_seats = self.rows * self.cols
        if total_seats < self.total_people:
            raise ValueError(f"座位不足！可用座位：{total_seats}，需容纳：{self.total_people}")
        
        # 混合参会人和空座并随机打乱
        empty_seats = ["空座"] * (total_seats - self.total_people)
        all_seats = self.name_list[:self.total_people] + empty_seats
        random.shuffle(all_seats)
        
        # 转换为二维列表（行×列）
        return [all_seats[i*self.cols : (i+1)*self.cols] for i in range(self.rows)]

    def _create_visual_plan(self):
        """生成基础可视化座位表（有人=○，空座=□）"""
        visual = []
        # 严格按座位表行列生成，确保一一对应
        for row in self.seating_plan:
            visual_row = []
            for seat in row:
                visual_row.append("○" if seat != "空座" else "□")
            visual.append(visual_row)
        return visual

    def _generate_seat_html(self, seat_type, is_target=False):
        """生成单个座位的HTML（统一封装，避免冗余）"""
        if seat_type == "○":
            color = "#27AE60"
            hover_color = "#219653"
            tip = "其他参会人"
            shadow = "none"
            symbol = "○"
        elif seat_type == "□":
            color = "#E74C3C"
            hover_color = "#C0392B"
            tip = "空座"
            shadow = "none"
            symbol = "□"
        elif seat_type == "⭐":
            color = "#F39C12"
            hover_color = "#E67E22"
            tip = "你的座位"
            shadow = "0 0 8px #F39C12"
            symbol = "⭐"
        else:
            color = "#95A5A6"
            hover_color = "#7F8C8D"
            tip = "未知座位"
            shadow = "none"
            symbol = "?"
        
        # 紧凑的HTML字符串（无多余换行/空格）
        html = f"""
<span title='{tip}' style='display:inline-block;width:35px;height:35px;line-height:35px;text-align:center;border:1px solid #ddd;border-radius:6px;margin:2px;background:{color};color:white;font-size:16px;transition:all 0.2s ease;cursor:pointer;box-shadow:{shadow};' onmouseover="this.style.background='{hover_color}'" onmouseout="this.style.background='{color}'">{symbol}</span>
"""
        # 移除所有多余换行和空格，避免排版错位
        return html.replace("\n", "").strip()

    def get_full_visual_html(self):
        """生成完整可视化座位表的HTML（紧凑排版，无多余换行）"""
        # 外层容器（紧凑写法，无多余换行）
        html = f"""
<div style='font-family:"Microsoft YaHei",Arial,sans-serif;line-height:1.8;margin:10px 0;padding:15px;background-color:#f8f9fa;border-radius:8px;'>
<h4 style='color:#2E86AB;margin-bottom:15px;font-weight:600;'>会议座位示意图（完整）</h4>
<div style='margin-bottom:10px;font-weight:bold;display:flex;align-items:center;'>
<span style='margin-right:10px;'>列：</span>
"""
        # 列号（紧凑生成，无多余换行）
        for i in range(self.cols):
            html += f"<span style='display:inline-block;width:35px;height:35px;line-height:35px;text-align:center;margin:0 1px;font-size:14px;'>{i+1}</span>"
        html += "</div>"
        
        # 每行座位（紧凑生成，无多余换行/空格）
        for row_idx, row in enumerate(self.visual_plan, 1):
            html += f"<div style='margin:8px 0;display:flex;align-items:center;line-height:40px;'><span style='width:50px;font-weight:500;'>行{row_idx}：</span>"
            for seat in row:
                html += self._generate_seat_html(seat)
            html += "</div>"
        
        # 说明文字
        html += """
<p style='margin-top:15px;font-size:12px;color:#666;padding-top:10px;border-top:1px solid #eee;'>
说明：○=已分配座位 | □=空座 | ⭐=你的座位
</p>
</div>
"""
        # 最终清理：移除所有多余的换行和空格
        return html.replace("\n", "").strip()

    def search_and_mark_seat(self, name):
        """查询姓名并返回标记后的结果和可视化HTML"""
        name = name.strip()
        if not name:
            return "请输入有效姓名！", ""
        
        # 查找匹配的座位（支持模糊搜索）
        match_positions = []
        for row_idx, row in enumerate(self.seating_plan, 1):
            for col_idx, seat in enumerate(row, 1):
                if seat != "空座" and name in seat:
                    match_positions.append((row_idx, col_idx, seat))
        
        if not match_positions:
            return f"未找到姓名包含「{name}」的参会人，请检查输入！", ""
        
        # 生成标记后的可视化表（带索引越界防护）
        marked_visual = [row.copy() for row in self.visual_plan]
        for row, col, full_name in match_positions:
            row_idx = row - 1
            col_idx = col - 1
            # 严格校验索引合法性
            if 0 <= row_idx < len(marked_visual) and 0 <= col_idx < len(marked_visual[row_idx]):
                marked_visual[row_idx][col_idx] = "⭐"
            else:
                return f"姓名「{full_name}」的座位坐标（第{row}行第{col}列）超出范围！", ""
        
        # 生成标记后的可视化HTML（紧凑排版）
        html = f"""
<div style='font-family:"Microsoft YaHei",Arial,sans-serif;line-height:1.8;margin:10px 0;padding:15px;background-color:#f8f9fa;border-radius:8px;'>
<h4 style='color:#E67E22;margin-bottom:15px;font-weight:600;'>你的座位示意图（⭐标记）</h4>
<div style='margin-bottom:10px;font-weight:bold;display:flex;align-items:center;'>
<span style='margin-right:10px;'>列：</span>
"""
        # 列号（紧凑生成）
        for i in range(self.cols):
            html += f"<span style='display:inline-block;width:35px;height:35px;line-height:35px;text-align:center;margin:0 1px;font-size:14px;'>{i+1}</span>"
        html += "</div>"
        
        # 每行座位（带标记，紧凑生成）
        for row_idx, row in enumerate(marked_visual, 1):
            html += f"<div style='margin:8px 0;display:flex;align-items:center;line-height:40px;'><span style='width:50px;font-weight:500;'>行{row_idx}：</span>"
            for seat in row:
                html += self._generate_seat_html(seat)
            html += "</div>"
        
        # 说明文字
        html += """
<p style='margin-top:15px;font-size:12px;color:#666;padding-top:10px;border-top:1px solid #eee;'>
说明：○=其他参会人 | □=空座 | ⭐=你的座位
</p>
</div>
"""
        # 清理多余换行和空格
        html = html.replace("\n", "").strip()
        
        # 生成查询结果文本
        result_text = "### 🎯 座位查询结果\n"
        for row, col, full_name in match_positions:
            result_text += f"- 姓名：{full_name} | 座位：第{row}行第{col}列\n"
        
        return result_text, html

    def export_full_plan(self):
        """生成可下载的完整座位表文本"""
        content = f"===== 会议座位表（生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}）=====\n\n"
        # 列号
        content += "列号：" + " ".join([f"{i+1:6d}" for i in range(self.cols)]) + "\n"
        # 每行座位
        for row_idx, row in enumerate(self.seating_plan, 1):
            content += f"第{row_idx}行：" + " | ".join([f"{seat:6s}" for seat in row]) + "\n"
        # 说明
        content += """
\n============================
说明：
1. ○=已分配座位 | □=空座 | ⭐=查询者座位
2. 可通过在线系统输入姓名模糊查询座位
3. 座位表随机生成，如有调整请以现场张贴为准
============================"""
        return content

# ===================== Streamlit Web界面 =====================
def main():
    # 页面基础配置
    st.set_page_config(
        page_title="会议座位查询系统",
        page_icon="🪑",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 全局样式优化
    st.markdown("""
    <style>
    /* 标题样式 */
    .main-title {
        font-size: 2.5rem;
        color: #2C3E50;
        text-align: center;
        margin-bottom: 20px;
        font-weight: 700;
    }
    /* 子标题样式 */
    .sub-title {
        font-size: 1.2rem;
        color: #7F8C8D;
        text-align: center;
        margin-bottom: 30px;
    }
    /* 按钮样式优化 */
    .stButton>button {
        background-color: #3498DB;
        color: white;
        border-radius: 8px;
        padding: 8px 20px;
        border: none;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #2980B9;
        transform: translateY(-1px);
    }
    /* 输入框样式 */
    .stTextInput>div>div>input {
        border-radius: 6px;
        border: 1px solid #ddd;
        padding: 8px 12px;
    }
    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
    }
    /* 侧边栏样式 */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    /* 修复flex布局溢出问题 */
    div[data-testid="stVerticalBlock"] > div {
        overflow-x: auto;
    }
    </style>
    """, unsafe_allow_html=True)

    # 页面标题
    st.markdown('<h1 class="main-title">🪑 会议座位查询系统（可视化版）</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">参会人可自助查询座位，支持姓名模糊搜索 | 组织者可配置座位参数</p>', unsafe_allow_html=True)
    st.divider()

    # 侧边栏：配置参数
    with st.sidebar:
        st.header("⚙️ 座位配置", anchor="config")
        st.warning("⚠️ 调整配置后会重新生成座位表", icon="ℹ️")
        
        # 核心参数（优化布局）
        col1, col2 = st.columns(2)
        with col1:
            TOTAL_PEOPLE = st.number_input(
                "参会总人数",
                min_value=1,
                max_value=200,
                value=30,
                step=1,
                help="需≤座位总数（行数×列数）"
            )
        with col2:
            ROWS = st.number_input(
                "座位行数",
                min_value=1,
                max_value=30,
                value=6,
                step=1,
                help="建议与会场实际行数一致"
            )
        COLS = st.number_input(
            "座位列数",
            min_value=1,
            max_value=30,
            value=6,
            step=1,
            help="建议与会场实际列数一致"
        )

        # 姓名列表配置
        st.subheader("📝 参会人姓名列表", anchor="names")
        name_text = st.text_area(
            "每行一个姓名（自动去空/去重）",
            value="""张三
李四
王五
赵六
孙七
周八
吴九
郑十
钱十一
冯十二
陈十三
褚十四
卫十五
蒋十六
沈十七
韩十八
杨十九
朱二十
秦二十一
尤二十二
许二十三
何二十四
吕二十五
施二十六
张二十七
孔二十八
曹二十九
严三十
华三十一
金三十二""",
            height=300,
            help="可直接粘贴姓名列表，多余姓名会被自动截断，不足会补充默认姓名"
        )
        # 解析姓名列表
        NAME_LIST = [line.strip() for line in name_text.split("\n") if line.strip()]

        # 重置按钮（兼容所有Streamlit版本）
        if st.button("🔄 重新生成座位表", type="secondary"):
            try:
                st.rerun()
            except AttributeError:
                st.experimental_rerun()

    # 初始化座位系统
    try:
        seating = VisualMeetingSeating(
            total_people=TOTAL_PEOPLE,
            rows=ROWS,
            cols=COLS,
            name_list=NAME_LIST
        )
        # 成功提示
        st.success(f"✅ 座位表生成成功！总座位数：{ROWS*COLS} | 参会人数：{TOTAL_PEOPLE}", icon="✅")

        # 主体内容：分栏展示
        tab1, tab2 = st.tabs(["📊 座位示意图", "🔍 座位查询"])

        with tab1:
            # 完整座位示意图
            st.subheader("完整座位分布", anchor="full-plan")
            st.markdown(seating.get_full_visual_html(), unsafe_allow_html=True)
            
            # 导出按钮
            export_content = seating.export_full_plan()
            st.download_button(
                label="📥 下载完整座位表（TXT）",
                data=export_content,
                file_name=f"会议座位表_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                help="下载后可打印张贴在会场",
                type="secondary"
            )

        with tab2:
            # 座位查询功能
            st.subheader("自助座位查询", anchor="search")
            col_search, col_btn = st.columns([3, 1])
            with col_search:
                name_input = st.text_input(
                    "请输入你的姓名（支持模糊搜索，如：张、李四）",
                    placeholder="例：张三、李、王十五",
                    label_visibility="collapsed"
                )
            with col_btn:
                search_btn = st.button("查询座位", type="primary", use_container_width=True)

            # 执行查询
            if search_btn:
                if name_input:
                    result_text, marked_html = seating.search_and_mark_seat(name_input)
                    st.markdown(result_text)
                    if marked_html:
                        st.markdown(marked_html, unsafe_allow_html=True)
                else:
                    st.warning("请输入姓名后再查询！", icon="⚠️")

    except ValueError as e:
        st.error(f"❌ 配置错误：{e}", icon="❌")
        st.info("请调整以下参数：\n1. 确保座位总数（行数×列数）≥参会人数\n2. 行数/列数必须为正整数", icon="ℹ️")

# ===================== 程序入口 =====================
if __name__ == "__main__":
    main()