import os

import psycopg2
import requests


class Activity:
    def __init__(
        self, id, title, objectives, goals, materials, difficulty, image, steps
    ):
        self.id = id
        self.title = title
        self.objectives = objectives
        self.goals = goals
        self.materials = materials
        self.difficulty = difficulty
        self.image = image
        self.steps = steps


class Step:
    def __init__(self, id, instructions, materials, image):
        self.id = id
        self.instructions = instructions
        self.materials = materials
        self.image = image


conn = psycopg2.connect(
    database=os.environ.get("PG_DATABASE"),
    host=os.environ.get("PG_HOST"),
    user=os.environ.get("PG_USER"),
    password=os.environ.get("PG_PASSWORD"),
    port=os.environ.get("PG_PORT"),
    sslmode=os.environ.get("PG_SSL"),
)

cursor = conn.cursor()

cursor.execute(
    "SELECT table1.id, table1.title, table1.objectives, table1.goals, table1.materials, table1.difficulty, table1.public_identifier, table2.id, table2.instructions, table2.materials, table2.public_identifier FROM (SELECT activities.id, activities.title, objectives, goals, activities.materials, difficulty, images.public_identifier FROM activities INNER JOIN images ON activities.id = images.imageable_id WHERE images.imageable_type = 'Activity' AND objectives != '' AND activities.availability = 'published') AS table1 INNER JOIN (SELECT steps.id, instructions, steps.materials, steps.activity_id, images.public_identifier FROM steps INNER JOIN images ON steps.id = images.imageable_id WHERE images.imageable_type = 'Step') AS table2 ON table1.id = table2.activity_id ORDER BY table1.id, table2.id;"
)

for i, row in enumerate(cursor.fetchall()):
    if i == 0:
        steps = []
        steps.append(Step(row[7], row[8], row[9], row[10]))
        activity_list = []
        activity_list.append(
            Activity(row[0], row[1], row[2], row[3], row[4], row[5], row[6], steps)
        )
    else:
        if activity_list[-1].id == row[0]:
            activity_list[-1].steps.append(Step(row[7], row[8], row[9], row[10]))

        else:
            steps = []
            steps.append(Step(row[7], row[8], row[9], row[10]))
            activity_list.append(
                Activity(row[0], row[1], row[2], row[3], row[4], row[5], row[6], steps)
            )

conn.close()

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("DATABASE_ID")
PAGE_ID = os.environ.get("PAGE_ID")

url = "https://api.notion.com/v1/pages"

headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content Type": "application/json",
    "Notion-Version": "2022-06-28",
}

for activity in activity_list:
    print(activity.title)
    print("https://res.cloudinary.com/ddlwdkxtf/image/upload/f_auto/" + activity.image)
    page_content = [
        {"type": "divider", "divider": {}},
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": ""},
                    }
                ]
            },
        },
        {
            "object": "block",
            "type": "image",
            "image": {
                "type": "external",
                "external": {
                    "url": "https://res.cloudinary.com/ddlwdkxtf/image/upload/f_auto/"
                    + activity.image
                    + ".png"
                },
            },
        },
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": "Objectives"},
                        "annotations": {
                            "bold": True,
                        },
                    }
                ]
            },
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": activity.objectives},
                    }
                ]
            },
        },
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": "Goals"},
                        "annotations": {
                            "bold": True,
                        },
                    }
                ]
            },
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": activity.goals},
                    }
                ]
            },
        },
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": "Materials"},
                        "annotations": {
                            "bold": True,
                        },
                    }
                ]
            },
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": activity.materials},
                    }
                ]
            },
        },
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": "Difficulty: "},
                        "annotations": {
                            "bold": True,
                        },
                    },
                    {
                        "type": "text",
                        "text": {"content": activity.difficulty.capitalize()},
                    },
                ]
            },
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": ""},
                    }
                ]
            },
        },
    ]

    for i, step in enumerate(activity.steps):
        page_content = page_content + [
            {"type": "divider", "divider": {}},
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": ""},
                        }
                    ]
                },
            },
            {
                "object": "block",
                "type": "image",
                "image": {
                    "type": "external",
                    "external": {
                        "url": "https://res.cloudinary.com/ddlwdkxtf/image/upload/f_auto/"
                        + step.image
                        + ".png"
                    },
                },
            },
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": f"Step {i + 1}"},
                            "annotations": {
                                "bold": True,
                            },
                        }
                    ]
                },
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": step.instructions},
                        },
                    ]
                },
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": ""},
                        }
                    ]
                },
            },
        ]

        if step.materials:
            page_content = page_content + [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": "Materials: "},
                                "annotations": {
                                    "bold": True,
                                },
                            },
                            {
                                "type": "text",
                                "text": {"content": step.materials},
                            },
                        ]
                    },
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": ""},
                            }
                        ]
                    },
                },
            ]

    payload = {
        "parent": {"page_id": PAGE_ID},
        "properties": {
            "title": {"title": [{"type": "text", "text": {"content": activity.title}}]}
        },
        "children": page_content,
    }

    response = requests.post(url, headers=headers, json=payload)
