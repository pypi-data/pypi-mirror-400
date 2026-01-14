"""\
论文阅读试验田 - 主程序
"""

import argparse
import shutil
from pathlib import Path
import re
import sys
import yaml


# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.moonshot_client import MoonshotClient
from src.paper.fetcher import PaperFetcher
from src.paper.parser import PaperParser
from src.knowledge.internalizer import KnowledgeInternalizer
from src.implementation.code_generator import CodeGenerator
from src.reading.glossary_extractor import GlossaryExtractor, GlossaryExplainer
from src.reading.guide_generator import GuideGenerator


def resolve_config_path(preferred: str = "config.yaml") -> str:
    """返回第一个存在的配置文件路径（兼容历史路径）。"""
    candidates = [
        preferred,
        "config.yaml",
        "config/config.yaml",
        "config",  # 兼容历史：仓库里可能存在一个名为 config 的 YAML 文件
    ]
    for p in candidates:
        if p and Path(p).exists():
            return p
    return preferred


def derive_paper_id(paper_path: str, paper_info: dict) -> str | None:
    """尽量从文件名中提取 arXiv ID；否则用标题生成一个稳定的目录名。"""
    # 文件名常见形式："2411.10825_xxx.pdf"；这里不要用 \b 以免被下划线打断。
    m = re.search(r"(\d{4}\.\d{5})", paper_path)
    if m:
        return m.group(1)


    title = (paper_info.get("title") or "").strip()
    if not title:
        return None

    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", title).strip("_")
    return safe[:50] or None


def _unique_path(dst: Path) -> Path:
    """若目标已存在，则自动添加后缀避免覆盖。"""
    if not dst.exists():
        return dst
    stem = dst.stem
    suffix = dst.suffix
    parent = dst.parent
    for i in range(1, 1000):
        cand = parent / f"{stem}__{i}{suffix}"
        if not cand.exists():
            return cand
    return parent / f"{stem}__{int(Path().stat().st_mtime)}{suffix}"


def _move_tree(src: Path, dst: Path, apply: bool, logs: list[str]):
    """将 src 目录内容合并/移动到 dst。"""
    if not src.exists():
        return

    if src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        final_dst = _unique_path(dst)
        logs.append(f"FILE  {src} -> {final_dst}")
        if apply:
            shutil.move(str(src), str(final_dst))
        return

    dst.mkdir(parents=True, exist_ok=True)

    for child in src.iterdir():
        target = dst / child.name
        if child.is_dir():
            _move_tree(child, target, apply, logs)
            if apply:
                # 尝试删除空目录
                try:
                    child.rmdir()
                except OSError:
                    pass
        else:
            final_target = _unique_path(target)
            logs.append(f"FILE  {child} -> {final_target}")
            if apply:
                final_target.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(child), str(final_target))

    if apply:
        try:
            src.rmdir()
        except OSError:
            pass


def migrate_data_layout(
    config_path: str,
    apply: bool = False,
    move_pdfs: bool = True,
    merge_aliases: bool = True,
):
    """把旧 `data/` 结构迁移到新结构：`data/papers/<paper_id>/...`。"""

    cfg: dict = {}
    if Path(config_path).exists():
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}

    pr = cfg.get("paper_reading", {}) if isinstance(cfg, dict) else {}
    workspace_root = Path(pr.get("paper_workspace_dir") or pr.get("output_root") or "data/papers")
    workspace_root.mkdir(parents=True, exist_ok=True)

    papers_dir = Path(pr.get("papers_dir") or "papers")
    papers_dir.mkdir(parents=True, exist_ok=True)

    data_root = Path("data")
    logs: list[str] = []

    # 1) 迁移按类型分桶的旧产物
    mapping = {
        "notes": (Path(pr.get("notes_dir") or "data/notes"), "notes"),
        "summaries": (Path(pr.get("summaries_dir") or "data/summaries"), "summaries"),
        "guides": (Path(pr.get("guides_dir") or "data/guides"), "guides"),
        "code": (Path(pr.get("code_dir") or "data/code"), "code"),
        "knowledge": (Path(pr.get("knowledge_dir") or "data/knowledge"), "knowledge"),
    }

    for _, (old_root, kind) in mapping.items():
        if not old_root.exists() or not old_root.is_dir():
            continue

        for item in list(old_root.iterdir()):
            if item.name in {".gitkeep"}:
                continue

            # data/papers 自己别动
            if item.name == "papers" and old_root == data_root:
                continue

            if item.is_dir():
                pid = item.name
                target_dir = workspace_root / pid / kind
                logs.append(f"DIR   {item} -> {target_dir}")
                _move_tree(item, target_dir, apply, logs)
            else:
                # 根目录散落文件 -> _unknown
                pid = "_unknown"
                target_file = workspace_root / pid / kind / item.name
                _move_tree(item, target_file, apply, logs)

        if apply:
            # 删除空的旧根目录
            try:
                old_root.rmdir()
            except OSError:
                pass

    # 2) 把 data 根目录里误放的 PDF 挪到 papers/
    if move_pdfs and data_root.exists():
        for pdf in data_root.glob("*.pdf"):
            dst = papers_dir / pdf.name
            final_dst = _unique_path(dst)
            logs.append(f"PDF   {pdf} -> {final_dst}")
            if apply:
                shutil.move(str(pdf), str(final_dst))

    # 2.5) 依据 papers/ 下的文件名，把历史的"标题目录"合并/重命名到 arXiv ID 目录
    # 例：papers/2411.10825_ARM_xxx.pdf 可能对应 data/papers/ARM_xxx/
    if merge_aliases and workspace_root.exists():
        arxiv_re = re.compile(r"(\d{4}\.\d{5})")
        for pdf in papers_dir.glob("*.pdf"):
            m = arxiv_re.search(pdf.name)
            if not m:
                continue
            arxiv_id = m.group(1)
            stem = pdf.stem
            # 去掉前缀 arxiv_id 以及紧跟的分隔符
            title_slug = re.sub(rf"^{re.escape(arxiv_id)}[_-]*", "", stem)
            if not title_slug:
                continue

            src = workspace_root / title_slug
            dst = workspace_root / arxiv_id
            if not src.exists() or src == dst:
                continue

            if dst.exists():
                logs.append(f"ALIAS {src} -> {dst}")
                _move_tree(src, dst, apply, logs)
            else:
                logs.append(f"DIR   {src} -> {dst}")
                if apply:
                    shutil.move(str(src), str(dst))

    # 3) 输出日志

    header = "[APPLY]" if apply else "[DRY-RUN]"
    print(header, f"workspace_root={workspace_root}")
    for line in logs:
        print(header, line)
    print(header, f"total_moves={len(logs)}")



def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="论文阅读试验田 - 使用 Moonshot AI 进行论文分析")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 获取 SIGGRAPH 信息
    subparsers.add_parser("fetch", help="获取 SIGGRAPH 网站信息")

    # 分析论文
    analyze_parser = subparsers.add_parser("analyze", help="分析论文")
    analyze_parser.add_argument("paper_path", help="论文文件路径")

    # 下载 PDF 到 papers/（支持任意 URL）
    download_parser = subparsers.add_parser("download", help="下载 PDF 到 papers_dir")
    download_parser.add_argument("url", help="PDF 链接")
    download_parser.add_argument("--name", default=None, help="保存文件名（可选）")

    analyze_parser.add_argument(
        "--type",
        choices=["comprehensive", "summary", "methodology", "innovation", "implementation"],
        default="comprehensive",
        help="分析类型",
    )

    # 完整流程
    full_parser = subparsers.add_parser("full", help="完整流程：分析、内化、落地")
    full_parser.add_argument("paper_path", help="论文文件路径")
    full_parser.add_argument("--language", choices=["python", "cpp"], default="python", help="代码实现语言")

    # 迁移 data 目录到新结构
    migrate_parser = subparsers.add_parser("migrate-data", help="迁移旧 data/ 目录到按论文隔离的新结构")
    migrate_parser.add_argument("--apply", action="store_true", help="实际执行迁移（默认仅预览）")
    migrate_parser.add_argument("--no-move-pdfs", action="store_true", help="不移动 data 根目录中的 PDF 到 papers/")
    migrate_parser.add_argument("--no-merge-aliases", action="store_true", help="不把标题目录合并/重命名为 arXiv ID 目录")



    args = parser.parse_args()

    if args.command == "migrate-data":
        config_path = resolve_config_path("config.yaml")
        migrate_data_layout(
            config_path=config_path,
            apply=bool(getattr(args, "apply", False)),
            move_pdfs=not bool(getattr(args, "no_move_pdfs", False)),
            merge_aliases=not bool(getattr(args, "no_merge_aliases", False)),
        )

        return

    if args.command == "download":
        config_path = resolve_config_path("config.yaml")
        fetcher = PaperFetcher(config_path=config_path)
        saved = fetcher.download_pdf(args.url, filename=getattr(args, "name", None))
        if not saved:
            print("下载失败")
            return
        print(f"下载完成: {saved}")
        return

    if args.command == "fetch":


        fetcher = PaperFetcher()
        info = fetcher.fetch_siggraph_info()

        print("=" * 60)
        print("SIGGRAPH 网站信息")
        print("=" * 60)

        if isinstance(info, dict) and info.get("error"):
            print(f"[ERROR] {info.get('error')}")
            msg = info.get("message")
            if msg:
                print(f"提示: {msg}")
            return

        print(f"标题: {info.get('title', 'N/A')}")

        print(f"\n最新新闻 ({len(info.get('latest_news', []))} 条):")
        for news in info.get("latest_news", [])[:5]:
            print(f"  - {news.get('title', 'N/A')}")

        print(f"\n会议信息 ({len(info.get('conferences', []))} 条):")
        for conf in info.get("conferences", [])[:5]:
            print(f"  - {conf.get('title', 'N/A')}")

        print(f"\n论文相关链接 ({len(info.get('papers_links', []))} 条):")
        for link in info.get("papers_links", [])[:10]:
            print(f"  - {link.get('text', 'N/A')}: {link.get('url', 'N/A')}")

    elif args.command == "analyze":
        print(f"正在分析论文: {args.paper_path}")

        parser_obj = PaperParser()
        if args.paper_path.endswith(".pdf"):
            paper_data = parser_obj.parse_pdf(args.paper_path)
        else:
            with open(args.paper_path, "r", encoding="utf-8") as f:
                text = f.read()
            paper_data = parser_obj.parse_text(text)

        client = MoonshotClient()
        analysis = client.analyze_paper(paper_data.get("full_text", ""), args.type)

        print("\n" + "=" * 60)
        print("分析结果")
        print("=" * 60)
        print(analysis)

    elif args.command == "full":
        print(f"开始完整流程处理: {args.paper_path}")
        print("-" * 60)

        # 0. 如果传入的是 URL，先下载到 papers_dir
        config_path = resolve_config_path("config.yaml")
        if str(args.paper_path).startswith("http://") or str(args.paper_path).startswith("https://"):
            print("检测到 URL，先下载 PDF...")
            fetcher = PaperFetcher(config_path=config_path)
            downloaded = fetcher.download_pdf(str(args.paper_path))
            if not downloaded:
                print("下载失败，无法继续解析")
                return
            args.paper_path = str(downloaded)
            print(f"已下载到: {args.paper_path}")

        # 1. 解析论文
        print("步骤 1/5: 解析论文...")
        parser_obj = PaperParser()
        if args.paper_path.endswith(".pdf"):
            paper_data = parser_obj.parse_pdf(args.paper_path)

        else:
            with open(args.paper_path, "r", encoding="utf-8") as f:
                text = f.read()
            paper_data = parser_obj.parse_text(text)

        paper_info = {
            "title": paper_data.get("title", "Unknown"),
            "authors": paper_data.get("authors", []),
            "abstract": paper_data.get("abstract", ""),
        }
        paper_id = derive_paper_id(args.paper_path, paper_info)
        print(f"  论文标题: {paper_info['title']}")
        if paper_id:
            print(f"  paper_id: {paper_id}")

        # 加载读者配置
        config: dict = {}

        if Path(config_path).exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}

        reader_profile = config.get("reader_profile", {})
        reader_type = reader_profile.get("type", "amateur")
        reader_config = reader_profile.get(reader_type, {}) if isinstance(reader_profile, dict) else {}

        # 2. AI 分析
        print("\n步骤 2/5: AI 分析论文...")
        client = MoonshotClient(config_path=config_path)

        print("  - 全面分析（根据读者背景调整）...")
        analysis = client.analyze_paper(
            paper_data.get("full_text", ""),
            "comprehensive",
            reader_profile=reader_profile if isinstance(reader_profile, dict) else None,
        )

        print("  - 提取关键点...")
        key_points = client.extract_key_points(paper_data.get("full_text", ""))

        print("  - 生成实现指南...")
        implementation_guide = client.generate_implementation_guide(paper_data.get("full_text", ""))

        # 2.5 辅助阅读：术语提取和解释 + 阅读指南
        glossary: dict = {}
        reading_guide_path = None
        if reader_config.get("needs_glossary", True):
            print("\n步骤 3/5: 辅助阅读处理...")
            print("  - 提取专有名词...")
            extractor = GlossaryExtractor(config_path)
            terms = extractor.extract_terms(paper_data.get("full_text", ""))
            print(f"  找到 {len(terms)} 个术语")

            if terms:
                print("  - 生成术语解释...")
                explainer = GlossaryExplainer(client)
                glossary = explainer.explain_terms_batch(terms, reader_config.get("background", ""))
                print(f"  已解释 {len(glossary)} 个术语")

            if reader_config.get("needs_guidance", True):
                print("  - 生成阅读指南...")
                guide_gen = GuideGenerator(config_path)
                reading_guide_path = guide_gen.generate_reading_guide(
                    paper_info,
                    analysis,
                    key_points if isinstance(key_points, dict) else {"raw_response": str(key_points)},
                    glossary,
                    client,
                    paper_id=paper_id,
                )
                if reading_guide_path:
                    print(f"  阅读指南已保存: {reading_guide_path}")

        # 4. 知识内化
        print("\n步骤 4/5: 知识内化...")
        internalizer = KnowledgeInternalizer(config_path=config_path)

        note_path = internalizer.create_note(
            paper_info,
            analysis,
            key_points if isinstance(key_points, dict) else {"raw_response": str(key_points)},
            paper_id=paper_id,
        )
        print(f"  笔记已保存: {note_path}")

        kg_entry = internalizer.create_knowledge_graph_entry(
            paper_info,
            key_points if isinstance(key_points, dict) else {"raw_response": str(key_points)},
        )
        internalizer.save_knowledge_graph([kg_entry], paper_id=paper_id, paper_info=paper_info)

        print("  知识图谱已更新")

        summary = internalizer.create_summary(paper_info, analysis)
        summaries_dir = internalizer.get_summaries_dir(paper_id=paper_id, paper_info=paper_info)

        summary_path = summaries_dir / "summary.md"
        summary_path.write_text(summary, encoding="utf-8")
        print(f"  摘要已保存: {summary_path}")

        # 5. 代码落地
        print("\n步骤 5/5: 生成代码框架...")
        code_gen = CodeGenerator(config_path=config_path)

        project_dir = code_gen.create_project_structure(
            paper_info["title"],
            implementation_guide,
            args.language,
            paper_id=paper_id,
        )
        print(f"  项目已创建: {project_dir}")

        implementation_guide_path = code_gen.save_implementation_guide(
            paper_info["title"],
            implementation_guide,
            paper_id=paper_id,
        )
        print(f"  实现指南已保存: {implementation_guide_path}")

        print("\n" + "=" * 60)
        print("处理完成！")
        print("=" * 60)
        print(f"笔记: {note_path}")
        print(f"代码: {project_dir}")
        print(f"摘要: {summary_path}")
        print(f"实现指南: {implementation_guide_path}")
        if reading_guide_path:
            print(f"阅读指南: {reading_guide_path}")
        if glossary:
            print(f"术语表: 已解释 {len(glossary)} 个术语（包含在阅读指南中）")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
