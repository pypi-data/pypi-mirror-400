import asyncio

from llama_cloud import AsyncLlamaCloud


async def parse_document() -> None:
    client = AsyncLlamaCloud()

    # Upload and parse a document, requdesting image content metadata
    result = await client.parsing.parse(
        upload_file="../example_files/attention_is_all_you_need.pdf",
        tier="agentic",
        version="latest",
        output_options={
            # Enable extraction of page screenshots
            "screenshots": {"enable": True},
            # Enable extraction of embedded images
            "embedded_images": {"enable": True},
        },
        expand=["images_content_metadata"],
    )

    print(result.items)


if __name__ == "__main__":
    asyncio.run(parse_document())
