from bluer_objects import README


items = README.Items(
    [
        {
            "name": f"feature {index}",
            "marquee": "https://github.com/kamangir/assets/raw/main/blue-plugin/marquee.png?raw=true",
            "description": f"description of feature {index} ...",
            "url": "./bluer_plugin/docs/feature_{}".format(
                index if index == 1 else f"{index}.md"
            ),
        }
        for index in range(1, 4)
    ]
)
