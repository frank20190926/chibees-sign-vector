# Chibees 矢量工程交付记录 — 2026-11-09

本轮按 Codex 的几何与印刷/CAD 分工完成本地生成；未提交比赛、发布站点或触碰其他项目改动。

## 入口

- 确定性生成器：`build_chibees_vectors.py`；运行 `python3 build_chibees_vectors.py`。
- 完整包：`exports/Chibees_Mexican_Restaurant_Master_Vector_Pack.zip`。
- 可嵌入展板的主图：`exports/Chibees_Sign_Exact_Cabinet_Preview.png`（2400×1800）。
- 透明图：`exports/Chibees_Sign_4K_Transparent.png`（4000×3000，300 DPI，白色描边属于图形）。
- 路径数据：`exports/Chibees_Master_Path_Data.json`。
- 参数/限制：`exports/README_Production.md`。
- 实测：`exports/Chibees_Verification_Report.json`。
- 最终视觉证据：`verification/Reference_vs_Reconstruction.png`、`verification/Edition_Proofs.jpg`、`verification/PDF_Proofs.jpg`、`verification/Monochrome_White_Proof.png`。
- 两次不同 PYTHONHASHSEED 下的逐文件哈希和 ZIP 一致性：`verification/rebuild_and_package_check.json`。

## 已核验

- 6 SVG 均零 text、零 image；路径仅 M/L/C/Z，所有字标和技术注释已转曲。
- 主艺术数据 7 图层、82 路径、106 子轮廓、741 个 M/L/C 端点命令、369 段三次曲线。锚点计数包括显式重复闭合端点，不等同于 Illustrator UI 的去重统计。
- 两个 e 共用同一源轮廓，仅平移 (+85,+11)，没有鼠标十字路径；双侧水滴依次红/绿/黄。
- 单色版使用单一 espresso 填色，无活动描边，全部闭合。
- AI：PDF 1.7 可解析，7 个 OCG 图层、82 矢量对象、零字体/图片；已渲染查看。
- 四页规格书：逐页渲染查看，零字体/图片，使用 DeviceCMYK。
- EPS：Level 3/CMYK 头、CMYK 操作符、82 路径和无字体/位图的结构检查通过；本机未找到 PostScript 解释器，未执行 EPS RIP 渲染。
- DXF：R2010/AC1024，106 条闭合 LWPOLYLINE，审计零错误，柜体 1270×2228.070175 mm；曲线离散弦误差上限 0.02 mm。
- 两次不同 Python 哈希种子重建后所有 17 个 exports 文件（含 ZIP）逐字节一致；ZIP CRC 与包内文件一致性通过。

## 后续协作边界

- 照片带屏幕摩尔纹及遮挡，细微纹理为依描述重建；不是原始设计文件的逐点复刻认证。
- 50 英寸按本轮要求解释为总柜高，开料前现场复核。DXF 是名义轮廓，颜色形状存在设计叠压，白色描边未做刀具偏移；CAM 需按用途选择/布尔合并、设刀径/补偿/深度。
- .ai 是真实 PDF 兼容分层交换文件，不含 Adobe 私有 AI 编辑数据；尚未在 Illustrator 中检查图层保留/回存。
- Pantone 485 C / 1795 C 是红色候选对色值，不是已测色结果，也未生成专色版。CMYK 文件未指定印厂 ICC、未宣称 PDF/X，印厂须打样确认。
- 生成依赖使用本机已有 fontTools/Pillow/PyMuPDF/ezdxf/rsvg-convert 与 Arial Bold，未安装依赖。ZIP 中的生成器按原工作区（含 ref 图片）重建。
- 已比较全局 AGENTS canonical 与 target 的措辞差异；本任务未改写/同步规则文件。

未启动后台服务、浏览器或子代理。核验用逐张中间渲染已汇总成上述证据图，临时文件按项目规则清理并登记。
