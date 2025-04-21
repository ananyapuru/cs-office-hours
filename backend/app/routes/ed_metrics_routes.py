import re
from ..auth import roles_required
from flask import Blueprint, request, jsonify
from collections import Counter

# a minimal list of common English stop‑words
STOPWORDS = {
    'a','an','and','the','to','in','is','it','of','for','on','that','this',
    'with','as','at','by','from','or','but','if','be','are','was','were',
    'so','you','your','we','they','their','what','which','when','how', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i','j','k','l','m','n','o','p',
    'q','r','s','t','u','v','x','y','z','1','2','3','4','5','6','7','8','9','0','i','my','not', 'can', 'have', 'just', 'test', 'do', 'code', 'process', 'function', 
    'do', 'there', 'output', 'process', 'hi', 'should', 'long'
}
ed_metrics_bp = Blueprint("ed_metrics", __name__)

def get_top_askers(posts, x):
    counter = Counter(
        p['user']['name']
        for p in posts
        if p.get('type') in ('post', 'question')
    )
    return [{'name': n, 'count': c} for n, c in counter.most_common(x)]



def get_top_answerers(posts, y, filters):
    """
    1. Always count any answer/comment that is `verified`.
    2. Always count any that is `endorsed`.
    3. Always count anything by a staff member (role!='student').
    4. Otherwise, only count if it:
       • meets min_length,
       • contains ALL include_words,
       • contains NONE of the exclude_words.
    """
    names = []
    print("Filters = ", filters)
    print("Min length = ", filters.get('min_length'))
    print("Include comments ? = ", filters.get('includeComments'))


    for p in posts:
        # start with answers
        bucket = list(p.get('answers', []))
        # optionally add comments
        if filters.get('includeComments'):
            bucket += p.get('comments', [])

        for ans in bucket:
            user = ans.get('user', {})
            text = ans.get('text', '')

            # 1) verified?
            if ans.get('verified', False):
                names.append(user['name'])
                continue

            # # 2) endorsed?
            if ans.get('endorsed', False):
                names.append(user['name'])
                continue

            # 3) staff?
            #    assume any role not exactly "student" is staff/ULA/instructor
            if user.get('role', '').lower() != 'student':
                names.append(user['name'])
                continue

            # 4) apply the remaining filters
            # length
            if len(text) < filters.get('min_length', 0):
                continue

            # include ALL include_words
            inc = filters.get('include_words', [])
            if inc and not all(w.lower() in text.lower() for w in inc):
                continue

            # exclude NONE of the exclude_words
            exc = filters.get('exclude_words', [])
            if exc and any(w.lower() in text.lower() for w in exc):
                continue

            # if we passed all of those, count it
            names.append(user['name'])

    # tally and return top y
    counter = Counter(names)
    return [
        {'name': n, 'count': c}
        for n, c in counter.most_common(y)
    ]


def get_common_words(posts, b):
    counter = Counter()
    for p in posts:
        words = re.findall(r"\b\w+\b", p.get('text', '').lower())
        filtered = [w for w in words if w not in STOPWORDS]
        counter.update(filtered)
    return [{'word': w, 'count': c} for w, c in counter.most_common(b)]


def get_common_tags(posts, top_n):
    counter = Counter()
    for p in posts:
        if cat := p.get('category'):
            counter[cat] += 1
        if sub := p.get('subcategory'):
            counter[sub] += 1
    return [{'tag': t, 'count': c} for t, c in counter.most_common(top_n)]


def get_top_viewed(posts, k):
    return sorted(posts, key=lambda p: p.get('views', 0), reverse=True)[:k]


@ed_metrics_bp.route("/edstem/metrics", methods=["POST"])
# @roles_required(['instructor', 'ULA'])
def compute_metrics():
    payload = request.get_json() or {}
    data = payload.get('data', [])
    params = payload.get('params', {})

    topAskX = params.get('topAskX', 5)
    topAnsY = params.get('topAnsY', 5)
    answerFilters = params.get('answerFilters', {})
    commonWordB = params.get('commonWordB', 10)
    topTagCount = params.get('topTagCount', 5)
    topViewedK = params.get('topViewedK', 5)

    top_askers   = get_top_askers(data, topAskX)
    top_answerers= get_top_answerers(data, topAnsY, answerFilters)
    common_words = get_common_words(
        [p for p in data if p.get('type') == 'question'],
        commonWordB
    )
    common_tags  = get_common_tags(
        [p for p in data if p.get('type') == 'question'],
        topTagCount
    )
    most_viewed  = get_top_viewed(data, topViewedK)

    return jsonify({
        'topAskers':    top_askers,
        'topAnswerers': top_answerers,
        'commonWords':  common_words,
        'commonTags':   common_tags,
        'mostViewed':   most_viewed
    }), 200
