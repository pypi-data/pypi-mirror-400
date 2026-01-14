docs = [
    {
        "path": "../docs/crawl",
    },
] + [
    {
        "path": f"../docs/crawl/{name}.md",
    }
    for name in [
        "one",
        "two",
        "three",
    ]
]
