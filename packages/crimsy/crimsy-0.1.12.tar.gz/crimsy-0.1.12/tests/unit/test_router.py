from crimsy.router import Router


async def test_router_prefix() -> None:
    router = Router(
        prefix="/",
    )

    assert router._prefix == "/"
