from pydivsufsort import divsufsort, kasai, most_frequent_substrings

K = 3
s = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum."  # noqa

sa = divsufsort(s)
lcp = kasai(s, sa)
pos, cnt = most_frequent_substrings(lcp, K, limit=10, minimum_count=5)

for p, c in zip(sa[pos], cnt):
    print(f"{s[p:p+K]!r} appeared {c} times")
