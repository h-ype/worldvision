"""
images 폴더 안의 이미지를 일괄 처리하는 스크립트

- .jpg / .jpeg : 용량 압축 (같은 폴더에 원본 덮어쓰지 않고 백업 후 압축)
- .png         : .webp로 변환

사용법:
    python optimize_images.py
    python optimize_images.py --dir images --quality 80 --webp-quality 80
    python optimize_images.py --keep-original   # 원본 유지하고 새 파일만 생성
"""

import argparse
import shutil
from pathlib import Path

from PIL import Image

JPG_EXTS = {".jpg", ".jpeg"}
PNG_EXTS = {".png"}


def compress_jpg(path: Path, quality: int, keep_original: bool, backup_dir: Path) -> None:
    img = Image.open(path)
    img = img.convert("RGB")  # JPEG는 알파 채널 미지원

    if keep_original:
        # 원본은 그대로 두고 _compressed 파일을 새로 만든다
        out_path = path.with_name(f"{path.stem}_compressed{path.suffix}")
    else:
        # 원본을 백업 폴더로 옮긴 뒤 같은 이름으로 압축본을 저장한다
        backup_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup_dir / path.name)
        out_path = path

    before = path.stat().st_size
    img.save(out_path, format="JPEG", quality=quality, optimize=True)
    after = out_path.stat().st_size

    print(
        f"[JPG 압축] {path.name}: {before/1024:.1f}KB -> {after/1024:.1f}KB "
        f"({(1 - after/before)*100:.1f}% 감소)"
    )


def convert_png_to_webp(path: Path, quality: int, keep_original: bool) -> None:
    img = Image.open(path)
    out_path = path.with_suffix(".webp")

    before = path.stat().st_size
    img.save(out_path, format="WEBP", quality=quality, method=6)
    after = out_path.stat().st_size

    print(
        f"[PNG->WEBP 변환] {path.name} -> {out_path.name}: "
        f"{before/1024:.1f}KB -> {after/1024:.1f}KB"
    )

    if not keep_original:
        path.unlink()


def main():
    parser = argparse.ArgumentParser(description="JPG 압축 / PNG -> WEBP 변환")
    parser.add_argument("--dir", default="images", help="이미지 폴더 경로 (기본값: images)")
    parser.add_argument("--quality", type=int, default=80, help="JPG 압축 품질 1-95 (기본값: 80)")
    parser.add_argument("--webp-quality", type=int, default=80, help="WEBP 품질 1-100 (기본값: 80)")
    parser.add_argument(
        "--keep-original",
        action="store_true",
        help="원본 파일을 삭제/백업하지 않고 그대로 둠 (jpg는 _compressed 파일 별도 생성)",
    )
    args = parser.parse_args()

    target_dir = Path(args.dir)
    if not target_dir.exists():
        print(f"폴더를 찾을 수 없습니다: {target_dir.resolve()}")
        return

    backup_dir = target_dir / "_originals_backup"

    files = sorted(target_dir.iterdir())
    if not files:
        print(f"{target_dir} 폴더에 이미지가 없습니다.")
        return

    jpg_count = 0
    png_count = 0

    for f in files:
        if not f.is_file():
            continue
        ext = f.suffix.lower()
        if ext in JPG_EXTS:
            compress_jpg(f, args.quality, args.keep_original, backup_dir)
            jpg_count += 1
        elif ext in PNG_EXTS:
            convert_png_to_webp(f, args.webp_quality, args.keep_original)
            png_count += 1

    print(f"\n완료: JPG {jpg_count}개 압축, PNG {png_count}개 WEBP 변환")
    if not args.keep_original and jpg_count:
        print(f"원본 JPG는 {backup_dir} 폴더에 백업되어 있습니다.")


if __name__ == "__main__":
    main()
