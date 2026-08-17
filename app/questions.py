"""設問データと5段階選択肢の定義

小学校低学年でも読めるよう、表示用テキストには <ruby> タグでふりがなを付けている。
（保存・集計用の CATEGORY_LABELS はふりがな無しの素の表記のまま）
"""

import re

_RUBY_RT_RE = re.compile(r"<rt>.*?</rt>")
_RUBY_TAG_RE = re.compile(r"</?ruby>")


def strip_ruby(html_text: str) -> str:
    """<ruby>タグ付きテキストからふりがなを除いた素のテキストを取り出す（CSV等の非HTML出力用）"""
    text = _RUBY_RT_RE.sub("", html_text)
    return _RUBY_TAG_RE.sub("", text)

CATEGORY_LABELS = {
    "nature": "自然志向",
    "inquiry": "探究心",
    "creativity": "創造性",
    "cooperation": "協調性",
    "action": "行動力",
}

CATEGORY_LABELS_RUBY = {
    "nature": "<ruby>自然志向<rt>しぜんしこう</rt></ruby>",
    "inquiry": "<ruby>探究心<rt>たんきゅうしん</rt></ruby>",
    "creativity": "<ruby>創造性<rt>そうぞうせい</rt></ruby>",
    "cooperation": "<ruby>協調性<rt>きょうちょうせい</rt></ruby>",
    "action": "<ruby>行動力<rt>こうどうりょく</rt></ruby>",
}

CATEGORY_ORDER = ["nature", "inquiry", "creativity", "cooperation", "action"]

QUESTIONS = [
    {"id": 1, "category": "nature", "text": "<ruby>公園<rt>こうえん</rt></ruby>や<ruby>森<rt>もり</rt></ruby>で<ruby>遊<rt>あそ</rt></ruby>ぶのが<ruby>好<rt>す</rt></ruby>きだ"},
    {"id": 2, "category": "nature", "text": "<ruby>虫<rt>むし</rt></ruby>や<ruby>植物<rt>しょくぶつ</rt></ruby>を<ruby>見<rt>み</rt></ruby>つけると、うれしくなる"},
    {"id": 3, "category": "nature", "text": "どろんこや<ruby>水遊<rt>みずあそ</rt></ruby>びをするのが<ruby>楽<rt>たの</rt></ruby>しい"},
    {"id": 4, "category": "nature", "text": "<ruby>休日<rt>きゅうじつ</rt></ruby>は<ruby>家<rt>いえ</rt></ruby>の<ruby>中<rt>なか</rt></ruby>より<ruby>外<rt>そと</rt></ruby>で<ruby>過<rt>す</rt></ruby>ごしたい"},
    {"id": 5, "category": "inquiry", "text": "「なんで？」「どうして？」と<ruby>考<rt>かんが</rt></ruby>えるのが<ruby>好<rt>す</rt></ruby>きだ"},
    {"id": 6, "category": "inquiry", "text": "<ruby>知<rt>し</rt></ruby>らないことを<ruby>調<rt>しら</rt></ruby>べたり、<ruby>聞<rt>き</rt></ruby>いたりするのが<ruby>楽<rt>たの</rt></ruby>しい"},
    {"id": 7, "category": "inquiry", "text": "<ruby>新<rt>あたら</rt></ruby>しい<ruby>実験<rt>じっけん</rt></ruby>や<ruby>工作<rt>こうさく</rt></ruby>にチャレンジしてみたい"},
    {"id": 8, "category": "inquiry", "text": "ふしぎなことを<ruby>見<rt>み</rt></ruby>つけると、もっと<ruby>知<rt>し</rt></ruby>りたくなる"},
    {"id": 9, "category": "creativity", "text": "<ruby>絵<rt>え</rt></ruby>をかいたり、<ruby>何<rt>なに</rt></ruby>かを<ruby>作<rt>つく</rt></ruby>ったりするのが<ruby>好<rt>す</rt></ruby>きだ"},
    {"id": 10, "category": "creativity", "text": "<ruby>自分<rt>じぶん</rt></ruby>だけのアイデアを<ruby>考<rt>かんが</rt></ruby>えるのが<ruby>楽<rt>たの</rt></ruby>しい"},
    {"id": 11, "category": "creativity", "text": "「こんなものがあったらいいな」を<ruby>想像<rt>そうぞう</rt></ruby>するのが<ruby>好<rt>す</rt></ruby>きだ"},
    {"id": 12, "category": "creativity", "text": "いつもと<ruby>違<rt>ちが</rt></ruby>うやり<ruby>方<rt>かた</rt></ruby>を<ruby>試<rt>ため</rt></ruby>してみたい"},
    {"id": 13, "category": "cooperation", "text": "みんなで<ruby>力<rt>ちから</rt></ruby>を<ruby>合<rt>あ</rt></ruby>わせて<ruby>何<rt>なに</rt></ruby>かをするのが<ruby>好<rt>す</rt></ruby>きだ"},
    {"id": 14, "category": "cooperation", "text": "<ruby>友<rt>とも</rt></ruby>だちが<ruby>困<rt>こま</rt></ruby>っていたら、<ruby>助<rt>たす</rt></ruby>けてあげたい"},
    {"id": 15, "category": "cooperation", "text": "グループで<ruby>話<rt>はな</rt></ruby>し<ruby>合<rt>あ</rt></ruby>って<ruby>決<rt>き</rt></ruby>めるのが<ruby>楽<rt>たの</rt></ruby>しい"},
    {"id": 16, "category": "cooperation", "text": "<ruby>誰<rt>だれ</rt></ruby>かと<ruby>一緒<rt>いっしょ</rt></ruby>にやるほうが、<ruby>一人<rt>ひとり</rt></ruby>でやるよりも<ruby>楽<rt>たの</rt></ruby>しい"},
    {"id": 17, "category": "action", "text": "<ruby>気<rt>き</rt></ruby>になったことは、すぐにやってみたい"},
    {"id": 18, "category": "action", "text": "<ruby>難<rt>むずか</rt></ruby>しそうなことでも、まずチャレンジしてみる"},
    {"id": 19, "category": "action", "text": "じっとしているより、<ruby>体<rt>からだ</rt></ruby>を<ruby>動<rt>うご</rt></ruby>かすほうが<ruby>好<rt>す</rt></ruby>きだ"},
    {"id": 20, "category": "action", "text": "<ruby>新<rt>あたら</rt></ruby>しい<ruby>場所<rt>ばしょ</rt></ruby>に<ruby>行<rt>い</rt></ruby>くと、わくわくする"},
]

TOTAL_QUESTIONS = len(QUESTIONS)

CHOICES = [
    {"value": 5, "label": "とてもそう<ruby>思<rt>おも</rt></ruby>う", "emoji": "🤩"},
    {"value": 4, "label": "そう<ruby>思<rt>おも</rt></ruby>う", "emoji": "😄"},
    {"value": 3, "label": "どちらともいえない", "emoji": "😊"},
    {"value": 2, "label": "あまりそう<ruby>思<rt>おも</rt></ruby>わない", "emoji": "🙂"},
    {"value": 1, "label": "そう<ruby>思<rt>おも</rt></ruby>わない", "emoji": "😐"},
]
