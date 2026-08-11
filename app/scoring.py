"""スコアリング・ヒーロータイプ決定ロジック"""

from itertools import combinations

from .questions import CATEGORY_ORDER, QUESTIONS

# "name" はDB保存・管理画面表示用の素の表記。
# "name_ruby" / "catch" は子供向け結果画面表示用で、<ruby>タグでふりがなを付けている。
HEROES = {
    frozenset({"nature", "inquiry"}): {
        "slug": "mori_science_ranger",
        "name": "森のサイエンスレンジャー",
        "name_ruby": "<ruby>森<rt>もり</rt></ruby>のサイエンスレンジャー",
        "catch": "<ruby>森<rt>もり</rt></ruby>のふしぎを<ruby>解<rt>と</rt></ruby>き<ruby>明<rt>あ</rt></ruby>かす<ruby>天才<rt>てんさい</rt></ruby>！",
        "color": "#2e7d32",
        "emoji": "🔬",
    },
    frozenset({"nature", "creativity"}): {
        "slug": "green_creator",
        "name": "グリーンクリエイター",
        "name_ruby": "グリーンクリエイター",
        "catch": "<ruby>自然<rt>しぜん</rt></ruby>からアイデアを<ruby>生<rt>う</rt></ruby>み<ruby>出<rt>だ</rt></ruby>すよ！",
        "color": "#43a047",
        "emoji": "🌿",
    },
    frozenset({"nature", "cooperation"}): {
        "slug": "forest_guardian",
        "name": "フォレストガーディアン",
        "name_ruby": "フォレストガーディアン",
        "catch": "みんなと<ruby>森<rt>もり</rt></ruby>を<ruby>守<rt>まも</rt></ruby>る<ruby>守護者<rt>しゅごしゃ</rt></ruby>！",
        "color": "#1b5e20",
        "emoji": "🛡️",
    },
    frozenset({"nature", "action"}): {
        "slug": "earth_adventure",
        "name": "アースアドベンチャー",
        "name_ruby": "アースアドベンチャー",
        "catch": "<ruby>地球<rt>ちきゅう</rt></ruby>を<ruby>駆<rt>か</rt></ruby>けまわる<ruby>冒険家<rt>ぼうけんか</rt></ruby>！",
        "color": "#558b2f",
        "emoji": "🌍",
    },
    frozenset({"inquiry", "creativity"}): {
        "slug": "mirai_hatsumei_hero",
        "name": "未来発明ヒーロー",
        "name_ruby": "<ruby>未来<rt>みらい</rt></ruby><ruby>発明<rt>はつめい</rt></ruby>ヒーロー",
        "catch": "<ruby>世界<rt>せかい</rt></ruby>を<ruby>変<rt>か</rt></ruby>える<ruby>発明<rt>はつめい</rt></ruby>を<ruby>生<rt>う</rt></ruby>み<ruby>出<rt>だ</rt></ruby>す！",
        "color": "#6a1b9a",
        "emoji": "💡",
    },
    frozenset({"inquiry", "cooperation"}): {
        "slug": "team_scientist",
        "name": "チームサイエンティスト",
        "name_ruby": "チームサイエンティスト",
        "catch": "<ruby>仲間<rt>なかま</rt></ruby>と<ruby>一緒<rt>いっしょ</rt></ruby>に<ruby>真実<rt>しんじつ</rt></ruby>を<ruby>探<rt>さぐ</rt></ruby>る！",
        "color": "#1565c0",
        "emoji": "🔭",
    },
    frozenset({"inquiry", "action"}): {
        "slug": "eco_explorer",
        "name": "エコエクスプローラー",
        "name_ruby": "エコエクスプローラー",
        "catch": "<ruby>行動<rt>こうどう</rt></ruby>しながら<ruby>学<rt>まな</rt></ruby>ぶ<ruby>探検家<rt>たんけんか</rt></ruby>！",
        "color": "#00838f",
        "emoji": "🧭",
    },
    frozenset({"creativity", "cooperation"}): {
        "slug": "machizukuri_creator",
        "name": "まちづくりクリエイター",
        "name_ruby": "まちづくりクリエイター",
        "catch": "みんなの<ruby>町<rt>まち</rt></ruby>を<ruby>楽<rt>たの</rt></ruby>しくデザイン！",
        "color": "#ef6c00",
        "emoji": "🏙️",
    },
    frozenset({"creativity", "action"}): {
        "slug": "dream_maker",
        "name": "ドリームメーカー",
        "name_ruby": "ドリームメーカー",
        "catch": "<ruby>夢<rt>ゆめ</rt></ruby>をすぐ<ruby>形<rt>かたち</rt></ruby>にする<ruby>実現力<rt>じつげんりょく</rt></ruby>！",
        "color": "#d81b60",
        "emoji": "✨",
    },
    frozenset({"cooperation", "action"}): {
        "slug": "smile_leader",
        "name": "スマイルリーダー",
        "name_ruby": "スマイルリーダー",
        "catch": "みんなを<ruby>笑顔<rt>えがお</rt></ruby>にする<ruby>行動派<rt>こうどうは</rt></ruby>リーダー！",
        "color": "#f9a825",
        "emoji": "😊",
    },
}

# 全カテゴリの組み合わせが定義されているか起動時に保証する
assert set(HEROES.keys()) == {frozenset(c) for c in combinations(CATEGORY_ORDER, 2)}


def compute_scores(answers: list[int]) -> tuple[dict[str, int], dict[str, int]]:
    """20問の回答（各1〜5）からカテゴリ別合計点と、タイブレーク用の単問最大点を算出する"""
    scores = {cat: 0 for cat in CATEGORY_ORDER}
    max_in_category = {cat: 0 for cat in CATEGORY_ORDER}
    for question, answer in zip(QUESTIONS, answers):
        cat = question["category"]
        scores[cat] += answer
        max_in_category[cat] = max(max_in_category[cat], answer)
    return scores, max_in_category


def determine_hero(scores: dict[str, int], max_in_category: dict[str, int]) -> dict:
    """得点上位2カテゴリからヒーロータイプを決定する（同点はタイブレークで解決）"""

    def sort_key(cat: str) -> tuple:
        # ①カテゴリ合計点 ②カテゴリ内の単問最大点 ③固定優先順位（CATEGORY_ORDERの先頭ほど優先）
        return (scores[cat], max_in_category[cat], -CATEGORY_ORDER.index(cat))

    ranked = sorted(CATEGORY_ORDER, key=sort_key, reverse=True)
    top_two = frozenset(ranked[:2])
    hero = HEROES[top_two]
    return {
        "categories": sorted(top_two, key=CATEGORY_ORDER.index),
        **hero,
    }
