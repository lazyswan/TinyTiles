#!/usr/bin/env python3
import argparse
import glob
import json
import re
from pathlib import Path
from typing import Any, Dict, List


def extract_number(path: str) -> int:
    m = re.search(r'scene-(\d+)\.json$', Path(path).name, re.IGNORECASE)
    return int(m.group(1)) if m else 9999


def load_json(path: Path) -> Any:
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def save_json(path: Path, obj: Any) -> None:
    with path.open('w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')


def is_event_like(line: Dict[str, Any]) -> bool:
    sm = str(line.get('speaker_marathi', '')).strip().lower()
    se = str(line.get('speaker_english', '')).strip().lower()
    if line.get('event'):
        return True
    return sm in {'event', '(music)'} or se in {'event', '(music)'}


def has_display_text(line: Dict[str, Any]) -> bool:
    return any(str(line.get(k, '')).strip() for k in ('english', 'marathi', 'event'))


def merge_block_items(lines: List[Dict[str, Any]], merge_same_speaker: bool = True) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for line in lines:
        item = {
            'source_line_index': line.get('line_index'),
            'speaker_marathi': line.get('speaker_marathi', ''),
            'speaker_english': line.get('speaker_english', ''),
            'marathi': line.get('marathi', ''),
            'english': line.get('english', ''),
            'event': line.get('event', ''),
            'is_event': is_event_like(line),
        }

        if not merge_same_speaker or item['is_event']:
            items.append(item)
            continue

        prev = items[-1] if items else None
        if (
            prev
            and not prev.get('is_event')
            and prev.get('speaker_marathi', '') == item.get('speaker_marathi', '')
            and prev.get('speaker_english', '') == item.get('speaker_english', '')
        ):
            if item.get('marathi'):
                prev['marathi'] = (
                    prev.get('marathi', '')
                    + ('\n' if prev.get('marathi') else '')
                    + item['marathi']
                ).strip()
            if item.get('english'):
                prev['english'] = (
                    prev.get('english', '')
                    + ('\n' if prev.get('english') else '')
                    + item['english']
                ).strip()
            if item.get('event'):
                prev['event'] = (
                    prev.get('event', '')
                    + ('\n' if prev.get('event') else '')
                    + item['event']
                ).strip()
        else:
            items.append(item)

    return items


def block_scene(
    scene: Dict[str, Any],
    lines_per_block: int,
    include_events: bool,
    merge_same_speaker: bool
) -> Dict[str, Any]:
    source_lines = scene.get('lines', [])
    filtered: List[Dict[str, Any]] = []

    for line in source_lines:
        if not has_display_text(line):
            continue
        if not include_events and is_event_like(line):
            continue
        filtered.append(line)

    blocks: List[Dict[str, Any]] = []
    for block_idx, start in enumerate(range(0, len(filtered), lines_per_block), start=1):
        chunk = filtered[start:start + lines_per_block]
        items = merge_block_items(chunk, merge_same_speaker=merge_same_speaker)
        blocks.append({
            'block_index': block_idx,
            'from_line_index': chunk[0].get('line_index') if chunk else None,
            'to_line_index': chunk[-1].get('line_index') if chunk else None,
            'raw_line_count': len(chunk),
            'item_count': len(items),
            'items': items,
        })

    out = {
        'scene_index': scene.get('scene_index'),
        'scene_title': scene.get('scene_title', ''),
        'location': scene.get('location', ''),
        'notes': scene.get('notes', ''),
        'blocks': blocks,
    }
    return out


def load_source(args: argparse.Namespace) -> Dict[str, Any]:
    if args.input:
        data = load_json(Path(args.input))
        if not isinstance(data, dict) or 'scenes' not in data:
            raise ValueError('--input must point to a bundled JSON with a top-level "scenes" array')
        return data

    if args.scene_dir:
        scene_glob = str(Path(args.scene_dir) / 'scene-*.json')
    else:
        scene_glob = args.scene_glob

    scene_paths = sorted(glob.glob(scene_glob), key=extract_number)
    if not scene_paths:
        raise ValueError(f'No scene files matched: {scene_glob}')

    scenes = []
    for p in scene_paths:
        scene = load_json(Path(p))
        if isinstance(scene, dict) and 'scene_index' in scene:
            scenes.append(scene)
        else:
            print(f'Skipped {p} (missing scene_index)')

    scenes.sort(key=lambda s: s.get('scene_index', 0))
    return {
        'play_title': args.play_title,
        'language_primary': 'marathi',
        'language_secondary': 'english',
        'scenes': scenes,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Bundle TinyTitle scene JSON into fixed-size display blocks.')

    parser.add_argument(
        'scene_dir',
        nargs='?',
        help='Optional directory containing scene-*.json files, e.g. "." or "scenes"'
    )
    parser.add_argument('--input', help='Existing bundled script JSON with top-level scenes[]')
    parser.add_argument('--scene-glob', default='scene-*.json', help='Scene file glob when not using --input or scene_dir')
    parser.add_argument('--output', default='bundled-script.json', help='Output bundled block JSON')
    parser.add_argument('--lines', type=int, required=True, help='Display lines per block, e.g. 3')
    parser.add_argument('--play-title', default='Baaki', help='Play title when building from scene files')
    parser.add_argument('--include-events', action='store_true', help='Keep event-only lines in blocks')
    parser.add_argument('--no-merge-same-speaker', action='store_true', help='Do not merge adjacent same-speaker lines inside a block')

    args = parser.parse_args()

    if args.lines < 1:
        raise ValueError('--lines must be >= 1')

    src = load_source(args)
    scenes = src.get('scenes', [])

    blocked_scenes = [
        block_scene(
            scene,
            args.lines,
            include_events=args.include_events,
            merge_same_speaker=not args.no_merge_same_speaker
        )
        for scene in scenes
    ]

    out = {
        'play_title': src.get('play_title', args.play_title),
        'language_primary': src.get('language_primary', 'marathi'),
        'language_secondary': src.get('language_secondary', 'english'),
        'bundle_mode': 'fixed_blocks',
        'lines_per_block': args.lines,
        'include_events': bool(args.include_events),
        'merge_same_speaker': not args.no_merge_same_speaker,
        'scene_count': len(blocked_scenes),
        'scenes': blocked_scenes,
    }

    save_json(Path(args.output), out)
    print(f'Wrote {args.output}')
    print(f'Scenes: {len(blocked_scenes)} | lines_per_block: {args.lines}')
    for scene in blocked_scenes:
        print(f"  Scene {scene.get('scene_index')}: {len(scene.get('blocks', []))} blocks")


if __name__ == '__main__':
    main()