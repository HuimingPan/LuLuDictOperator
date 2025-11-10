"""Utilities for adjusting LuLuDict word star ratings based on CET4 coverage."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Set, Tuple

from src.luludict.client import LuLuDictClient
from config import Config


def load_word_list(path: Path, label: str) -> Set[str]:
	"""Load a vocabulary list into a lowercase set."""

	if not path.exists():
		raise FileNotFoundError(f"{label} word list not found at {path}")

	words: Set[str] = set()
	with path.open("r", encoding="utf-8") as handle:
		for line in handle:
			word = line.strip().lower()
			if word:
				words.add(word)

	if not words:
		raise ValueError(f"{label} word list at {path} appears to be empty.")

	return words


def parse_star(value: Any) -> int:
	"""Safely convert the star field into an integer."""

	if isinstance(value, bool):
		return int(value)

	try:
		return int(value)
	except (TypeError, ValueError):
		return 0


def iter_word_entries(
	client: LuLuDictClient,
	*,
	language: str,
	category_id: int,
	page_size: int,
	request_delay: float,
	max_pages: Optional[int] = None,
) -> Iterable[Dict[str, Any]]:
	"""Yield paginated word entries containing star metadata."""

	page = 0

	while True:
		if max_pages is not None and page > max_pages:
			break

		response = client.get_page_word_list(
			language=language,
			category_id=category_id,
			page=page,
			page_size=page_size,
		)

		data = response.get("data", []) if isinstance(response, dict) else []
		if not data:
			break

		for entry in data:
			if isinstance(entry, dict):
				yield entry

		page += 1

		if request_delay > 0:
			time.sleep(request_delay)


def determine_target_star(
	word: str,
	current_star: int,
	cet4_words: Set[str],
	cet6_words: Set[str],
) -> Tuple[int, str]:
	"""Determine the desired star score and reason for adjustment."""

	lowered = word.lower()

	if lowered in cet4_words:
		return 5, "cet4"

	if lowered in cet6_words:
		return 4, "cet6"

	if current_star == 5 or current_star == 4:
		return 3, "demote"

	return current_star, "none"


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
	"""Parse CLI arguments for the rating script."""

	base_dir = Path(__file__).resolve().parent
	default_cet4_path = base_dir / "CET42.txt"
	default_cet6_path = base_dir / "CET6.txt"

	parser = argparse.ArgumentParser(
		description="Update LuLuDict star ratings based on the CET4 vocabulary list.",
	)

	parser.add_argument(
		"--cet4-path",
		type=Path,
		default=default_cet4_path,
		help=f"Path to CET4 word list (default: {default_cet4_path})",
	)
	parser.add_argument(
		"--cet6-path",
		type=Path,
		default=default_cet6_path,
		help=f"Path to CET6 word list (default: {default_cet6_path})",
	)
	parser.add_argument(
		"--language",
		default=Config.DEFAULT_LANGUAGE,
		help=f"LuLuDict language code (default: {Config.DEFAULT_LANGUAGE})",
	)
	parser.add_argument(
		"--category-id",
		type=int,
		default=Config.DEFAULT_CATEGORY_ID,
		help=f"LuLuDict category identifier (default: {Config.DEFAULT_CATEGORY_ID})",
	)
	parser.add_argument(
		"--page-size",
		type=int,
		default=Config.DEFAULT_PAGE_SIZE,
		help=f"Number of words fetched per page (default: {Config.DEFAULT_PAGE_SIZE})",
	)
	parser.add_argument(
		"--max-pages",
		type=int,
		default=None,
		help="Optionally limit the number of pages fetched (inclusive).",
	)
	parser.add_argument(
		"--request-delay",
		type=float,
		default=Config.REQUEST_DELAY,
		help=f"Delay between API requests in seconds (default: {Config.REQUEST_DELAY}).",
	)
	parser.add_argument(
		"--update-delay",
		type=float,
		default=Config.REQUEST_DELAY,
		help=f"Delay between star updates in seconds (default: {Config.REQUEST_DELAY}).",
	)
	parser.add_argument(
		"--dry-run",
		action="store_true",
		help="Compute desired ratings without calling the API.",
	)

	return parser.parse_args(args=list(argv) if argv is not None else None)


def main(argv: Optional[Iterable[str]] = None) -> int:
	"""Entry point for rating words based on CET4 inclusion."""

	args = parse_args(argv)

	if not Config.LULUDICT_TOKEN:
		print("❌ LuLuDict token is missing. Populate keys.json or set LULUDICT_TOKEN.")
		return 1

	try:
		cet4_words = load_word_list(args.cet4_path, "CET4")
		cet6_words = load_word_list(args.cet6_path, "CET6")
	except (FileNotFoundError, ValueError) as error:
		print(f"❌ {error}")
		return 1

	client = LuLuDictClient()

	total_words = 0
	updates_applied = 0
	cet4_promotions = 0
	cet6_assignments = 0
	demoted_to_four = 0
	skipped = 0
	failures = 0

	print(f"📚 Loaded {len(cet4_words)} CET4 words from {args.cet4_path}.")
	print(f"📗 Loaded {len(cet6_words)} CET6 words from {args.cet6_path}.")
	if args.dry_run:
		print("🧪 Running in dry-run mode. No star ratings will be updated.")

	for entry in iter_word_entries(
		client,
		language=args.language,
		category_id=args.category_id,
		page_size=args.page_size,
		request_delay=max(args.request_delay, 0.0),
		max_pages=args.max_pages,
	):
		word = entry.get("word")
		if not word:
			continue

		total_words += 1

		current_star = parse_star(entry.get("star"))
		target_star, reason = determine_target_star(
			word,
			current_star,
			cet4_words,
			cet6_words,
		)

		if target_star == current_star:
			skipped += 1
			continue

		if args.dry_run:
			updates_applied += 1
			if reason == "cet4":
				cet4_promotions += 1
				print(f"⭐ (dry-run) '{word}': {current_star} ➜ {target_star} (CET4 word)")
			elif reason == "cet6":
				cet6_assignments += 1
				print(f"🌟 (dry-run) '{word}': {current_star} ➜ {target_star} (CET6 word)")
			else:
				demoted_to_four += 1
				print(f"⬇️ (dry-run) '{word}': {current_star} ➜ {target_star} (not in CET lists)")
			continue

		response = client.update_word_star(word, target_star, language=args.language)

		if "error" in response:
			failures += 1
			print(
				f"❌ Failed to update '{word}' ({current_star} ➜ {target_star}): {response['error']}"
			)
		else:
			updates_applied += 1
			if reason == "cet4":
				cet4_promotions += 1
				print(f"⭐ Updated '{word}' to star 5 (CET4 word).")
			elif reason == "cet6":
				cet6_assignments += 1
				print(f"🌟 Updated '{word}' to star 4 (CET6 word).")
			else:
				demoted_to_four += 1
				print(f"⬇️ Downgraded '{word}' from {current_star} to {target_star} (not in CET lists).")

		if args.update_delay > 0:
			time.sleep(args.update_delay)

	print("\n📊 Summary")
	print(f"Total words inspected: {total_words}")
	print(f"Updates applied: {updates_applied}")
	print(f"  • Promoted to star 5 (CET4): {cet4_promotions}")
	print(f"  • Set to star 4 (CET6): {cet6_assignments}")
	print(f"  • Demoted from 5 to 4 (not in CET lists): {demoted_to_four}")
	print(f"Skipped (already correct): {skipped}")
	print(f"Failures: {failures}")

	return 0 if failures == 0 else 2


if __name__ == "__main__":
	sys.exit(main())


