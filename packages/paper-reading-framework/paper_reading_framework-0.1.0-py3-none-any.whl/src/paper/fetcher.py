"""\
论文获取模块
支持从 SIGGRAPH 等网站获取论文
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests
import yaml
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.exceptions import SSLError, Timeout, RequestException
from urllib3.util.retry import Retry



class PaperFetcher:
    """论文获取器"""

    def __init__(self, config_path: str = "config.yaml"):
        """初始化获取器。

        Args:
            config_path: 配置文件路径（支持 `config.yaml` / `config/config.yaml` / `config`）
        """
        self.config = self._load_config(config_path)
        self.siggraph_config = self.config.get("siggraph", {}) if isinstance(self.config, dict) else {}
        self.paper_reading_config = self.config.get("paper_reading", {}) if isinstance(self.config, dict) else {}

        self.base_url = self.siggraph_config.get("base_url", "https://www.siggraph.org")
        self.download_dir = Path(self.siggraph_config.get("download_dir", "papers/siggraph"))
        self.download_dir.mkdir(parents=True, exist_ok=True)

        # 通用论文下载默认输出目录（与项目其余模块保持一致）
        self.papers_dir = Path(self.paper_reading_config.get("papers_dir", "papers"))
        self.papers_dir.mkdir(parents=True, exist_ok=True)


        self.user_agent = self.siggraph_config.get(
            "user_agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        )
        self.verify_ssl = bool(self.siggraph_config.get("verify_ssl", True))

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件（兼容历史路径）。"""
        candidates = [config_path, "config.yaml", "config/config.yaml", "config"]
        for p in candidates:
            if not p:
                continue
            config_file = Path(p)
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
        return {}

    def fetch_siggraph_info(self) -> Dict[str, Any]:
        """获取 SIGGRAPH 网站信息。

        Returns:
            网站信息字典；失败时返回包含 `error` 与 `message` 的字典。
        """
        session = requests.Session()
        session.headers.update({"User-Agent": self.user_agent})

        base = self.base_url.rstrip("/")

        # 某些网络环境直连 https 可能触发 `WRONG_VERSION_NUMBER`；从 http 入口跳转往往更稳。
        urls_to_try: List[str] = [base]
        if base.startswith("https://"):
            urls_to_try = ["http://" + base[len("https://") :], base]
        elif base.startswith("http://"):
            urls_to_try = [base, "https://" + base[len("http://") :]]

        last_err: Optional[Exception] = None

        for url in urls_to_try:
            try:
                resp = session.get(
                    url,
                    timeout=10,
                    allow_redirects=True,
                    verify=self.verify_ssl,
                )
                resp.raise_for_status()

                soup = BeautifulSoup(resp.content, "html.parser")

                info: Dict[str, Any] = {
                    "title": soup.title.get_text(strip=True) if soup.title else "SIGGRAPH",
                    "description": "",
                    "latest_news": [],
                    "conferences": [],
                    "papers_links": [],
                    "final_url": resp.url,
                    "status_code": resp.status_code,
                }

                # 提取最新新闻（尽量宽松地匹配 class 中包含 news 的元素）
                news_sections = soup.find_all(["article", "div", "section"], class_=lambda x: x and "news" in x.lower())
                for section in news_sections[:8]:
                    title_elem = section.find(["h1", "h2", "h3", "h4", "a"])
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    if not title:
                        continue
                    href = ""
                    if getattr(title_elem, "name", "") == "a":
                        href = title_elem.get("href", "")
                    else:
                        a = section.find("a", href=True)
                        href = a.get("href", "") if a else ""
                    info["latest_news"].append({"title": title, "link": urljoin(resp.url, href) if href else ""})

                # 提取会议信息
                conf_sections = soup.find_all(["div", "section"], class_=lambda x: x and "conference" in x.lower())
                for section in conf_sections[:20]:
                    title_elem = section.find(["h1", "h2", "h3", "a"])
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    if not title:
                        continue
                    href = title_elem.get("href", "") if getattr(title_elem, "name", "") == "a" else ""
                    info["conferences"].append({"title": title, "link": urljoin(resp.url, href) if href else ""})

                # 查找论文相关链接
                links = soup.find_all("a", href=True)
                for link in links:
                    href = link.get("href", "")
                    text = link.get_text(strip=True)
                    if not text:
                        continue
                    if any(k in text.lower() for k in ["paper", "publication", "proceeding"]):
                        info["papers_links"].append({"text": text, "url": urljoin(resp.url, href)})

                return info

            except Exception as e:
                last_err = e
                # 轻微退避，避免瞬间重试
                time.sleep(0.2)

        return {"error": str(last_err) if last_err else "unknown", "message": "无法获取 SIGGRAPH 网站信息"}

    @staticmethod
    def _unique_path(dst: Path) -> Path:
        if not dst.exists():
            return dst
        stem = dst.stem
        suffix = dst.suffix
        parent = dst.parent
        for i in range(1, 1000):
            cand = parent / f"{stem}__{i}{suffix}"
            if not cand.exists():
                return cand
        return parent / f"{stem}__dup{suffix}"

    def download_pdf(self, url: str, filename: Optional[str] = None, output_dir: Optional[Path] = None, paper_id: Optional[str] = None) -> Optional[Path]:
        """通用下载：从任意 PDF URL 下载到 `papers_dir`（可指定 output_dir/filename）。
        
        Args:
            url: PDF 下载链接
            filename: 文件名（可选）
            output_dir: 输出目录（可选，默认使用 papers_dir）
            paper_id: 论文标识符（可选，如果提供则创建子文件夹 papers/<paper_id>/）
        
        改进：
        - 添加连接和读取超时控制（避免无限阻塞）
        - 添加下载进度显示
        - 添加 chunk 级别的超时检查
        - 自动清理中断的下载文件
        - 添加文件大小验证
        - 支持按论文ID创建子文件夹
        """
        base_dir = Path(output_dir) if output_dir is not None else self.papers_dir
        
        # 如果提供了 paper_id，创建子文件夹
        if paper_id:
            out_dir = base_dir / paper_id
        else:
            out_dir = base_dir
        
        out_dir.mkdir(parents=True, exist_ok=True)

        # 配置重试策略
        retry_strategy = Retry(
            total=2,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        
        session = requests.Session()
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update({"User-Agent": self.user_agent})

        urls_to_try: List[str] = [url]
        if url.startswith("https://"):
            urls_to_try = ["http://" + url[len("https://") :], url]
        elif url.startswith("http://"):
            urls_to_try = [url, "https://" + url[len("http://") :]]

        last_err: Optional[Exception] = None
        tmp_path: Optional[Path] = None

        for u in urls_to_try:
            try:
                # 连接超时 10 秒，读取超时 30 秒（每个 chunk 之间）
                # 总超时通过 chunk 超时控制
                print(f"正在连接: {u}")
                resp = session.get(
                    u, 
                    timeout=(10, 30),  # (connect_timeout, read_timeout)
                    stream=True, 
                    allow_redirects=True, 
                    verify=self.verify_ssl
                )
                resp.raise_for_status()

                # 获取文件大小（如果可用）
                total_size = int(resp.headers.get('content-length', 0))
                if total_size > 0:
                    print(f"文件大小: {total_size / 1024 / 1024:.2f} MB")

                # 文件名：优先用户传入，其次从 URL path 推断
                final_name = filename
                if not final_name:
                    parsed = urlparse(resp.url)
                    final_name = Path(parsed.path).name or "paper.pdf"

                if not final_name.lower().endswith(".pdf"):
                    final_name = final_name + ".pdf"

                filepath = self._unique_path(out_dir / final_name)
                tmp_path = filepath.with_suffix(filepath.suffix + ".part")
                
                # 清理可能存在的旧 .part 文件
                if tmp_path.exists():
                    tmp_path.unlink()

                print(f"开始下载: {final_name}")
                downloaded = 0
                chunk_size = 1024 * 256  # 256 KB
                last_chunk_time = time.time()
                chunk_timeout = 30  # 每个 chunk 最多等待 30 秒

                with open(tmp_path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=chunk_size):
                        current_time = time.time()
                        
                        # 检查 chunk 超时（如果超过 30 秒没有新数据，认为连接中断）
                        if current_time - last_chunk_time > chunk_timeout:
                            raise Timeout(f"下载超时：超过 {chunk_timeout} 秒没有接收到数据")
                        
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            last_chunk_time = current_time
                            
                            # 显示进度（每 1MB 或完成时）
                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                if downloaded % (1024 * 1024) < chunk_size or downloaded >= total_size:
                                    print(f"进度: {downloaded / 1024 / 1024:.2f} MB / {total_size / 1024 / 1024:.2f} MB ({percent:.1f}%)", end='\r')
                            else:
                                if downloaded % (1024 * 1024) < chunk_size:
                                    print(f"已下载: {downloaded / 1024 / 1024:.2f} MB", end='\r')

                print()  # 换行
                
                # 验证文件大小
                if total_size > 0 and tmp_path.stat().st_size != total_size:
                    raise ValueError(f"文件大小不匹配: 期望 {total_size}, 实际 {tmp_path.stat().st_size}")
                
                # 验证文件不为空
                if tmp_path.stat().st_size == 0:
                    raise ValueError("下载的文件为空")

                # 重命名为最终文件
                tmp_path.replace(filepath)
                print(f"下载完成: {filepath}")
                return filepath

            except (SSLError, Timeout, RequestException) as e:
                last_err = e
                # 清理中断的下载文件
                if tmp_path and tmp_path.exists():
                    try:
                        tmp_path.unlink()
                        print(f"已清理中断的下载文件: {tmp_path}")
                    except Exception:
                        pass
                print(f"尝试下一个 URL... ({type(e).__name__}: {e})")
                time.sleep(0.5)
            except Exception as e:
                last_err = e
                # 清理中断的下载文件
                if tmp_path and tmp_path.exists():
                    try:
                        tmp_path.unlink()
                        print(f"已清理中断的下载文件: {tmp_path}")
                    except Exception:
                        pass
                print(f"下载出错: {type(e).__name__}: {e}")
                time.sleep(0.5)

        print(f"下载失败: {last_err}")
        return None

    # 兼容旧接口名
    def download_paper(self, url: str, filename: Optional[str] = None) -> Optional[Path]:
        """下载论文（兼容旧方法，默认落到 `papers_dir`）。"""
        return self.download_pdf(url=url, filename=filename, output_dir=self.papers_dir)


    def download_arxiv_paper(self, arxiv_id: str) -> Optional[Path]:
        """从 arXiv 下载论文。

        Args:
            arxiv_id: arXiv ID，例如 "2504.12908" 或完整 URL

        Returns:
            下载的文件路径
        """
        try:
            if arxiv_id.startswith("http"):
                if "/abs/" in arxiv_id:
                    arxiv_id = arxiv_id.split("/abs/")[-1]
                elif "/pdf/" in arxiv_id:
                    arxiv_id = arxiv_id.split("/pdf/")[-1].replace(".pdf", "")

            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

            print(f"正在从 arXiv 下载论文: {arxiv_id}")
            print(f"下载链接: {pdf_url}")

            abs_url = f"https://arxiv.org/abs/{arxiv_id}"
            resp = requests.get(abs_url, timeout=10, headers={"User-Agent": self.user_agent})
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, "html.parser")

            # 使用 arXiv ID 作为论文标识符，创建独立子文件夹
            papers_dir = Path(self.config.get("paper_reading", {}).get("papers_dir", "papers"))
            papers_dir.mkdir(parents=True, exist_ok=True)
            
            # 文件名简化为 paper.pdf（因为已经在子文件夹中）
            filename = "paper.pdf"
            
            # 使用 arXiv ID 作为 paper_id，创建子文件夹 papers/<arxiv_id>/
            filepath = self.download_pdf(pdf_url, filename=filename, output_dir=papers_dir, paper_id=arxiv_id)
            if not filepath:
                return None

            print(f"下载完成: {filepath}")
            return filepath


        except Exception as e:
            print(f"下载失败: {e}")
            import traceback

            traceback.print_exc()
            return None

    def search_papers(self, keywords: List[str], year: Optional[int] = None) -> List[Dict[str, str]]:
        """搜索论文（占位方法，实际需要根据SIGGRAPH网站结构调整）。"""
        return []
