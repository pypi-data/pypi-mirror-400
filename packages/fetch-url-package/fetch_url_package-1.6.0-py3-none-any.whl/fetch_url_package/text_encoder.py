import re
from charset_normalizer import from_bytes

_META_CHARSET_RE = re.compile(
    br'<meta[^>]+charset=["\']?\s*([a-zA-Z0-9._\-]+)',
    re.IGNORECASE
)

_META_HTTP_EQUIV_RE = re.compile(
    br'<meta[^>]+http-equiv=["\']?content-type["\']?[^>]*>',
    re.IGNORECASE
)

_CHARSET_IN_CONTENT_RE = re.compile(
    br'charset\s*=\s*([a-zA-Z0-9._\-]+)',
    re.IGNORECASE
)

async def parse_encoder(resp):
    # 不能只用一部分去解码，strict模式下大概率会崩，需要网页全文解码
    content = resp.content
    # head = resp.content if _HEAD_SLICE is None else resp.content[:_HEAD_SLICE]
    # =========================================================
    # 1️⃣ HTTP Header charset（最高优先级）
    # =========================================================
    if resp.encoding:
        try:
            # print(f"Trying HTTP header encoding: {resp.encoding}")
            return content.decode(resp.encoding, errors="strict")
        except Exception:
            pass
    # =========================================================
    # 2️⃣ HTML <meta charset> / http-equiv
    # =========================================================
    m = _META_CHARSET_RE.search(content)
    if m:
        enc = m.group(1).decode("ascii", errors="ignore")
        try:
            # print(f"Trying HTML meta charset encoding: {enc}")
            return content.decode(enc, errors="strict")
        except Exception:
            pass

    if _META_HTTP_EQUIV_RE.search(content):
        m = _CHARSET_IN_CONTENT_RE.search(content)
        if m:
            enc = m.group(1).decode("ascii", errors="ignore")
            try:
                # print(f"Trying HTML meta http-equiv charset encoding: {enc}")
                return content.decode(enc, errors="strict")
            except Exception:
                pass
    # 如果有中文字符则尝试gbk编码
    if b'\xe4' in content or b'\xbf' in content or b'\xd6' in content:
        try:
            # print("Trying GBK encoding due to presence of Chinese characters")
            return content.decode("gbk", errors="strict")
        except Exception:
            pass
    # =========================================================
    # 3️⃣ BOM + 统计模型（charset-normalizer）
    # =========================================================
    best = from_bytes(content).best()
    if best and best.encoding:
        try:
            # print(f"Trying charset-normalizer encoding: {best.encoding}")
            return str(best)
        except Exception:
            pass

    # =========================================================
    # 4️⃣ 工业兜底（永不崩）
    # =========================================================
    try:
        # print("Trying fallback encoding: utf-8 with replace errors")
        return content.decode("utf-8", errors="replace")
    except Exception:
        # print("Trying fallback encoding: latin-1 with replace errors")
        return content.decode("latin-1", errors="replace")