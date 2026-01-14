"""
소양강댐 하류 수위 예측 템플릿

소양강댐의 방류량이 하류 의암댐 수위에 미치는 영향을 분석하기 위한 템플릿입니다.
약 5.5시간의 시차를 고려하여 데이터를 정렬합니다.

Usage:
    >>> import asyncio
    >>> from kdm_sdk.templates import load_python
    >>>
    >>> async def main():
    >>>     template = load_python("examples/templates/soyang_downstream.py")
    >>>     result = await template.execute()
    >>>
    >>>     # Analyze correlation
    >>>     if hasattr(result, 'calculate_correlation'):
    >>>         corr_result = result.calculate_correlation(lag_hours=5.5)
    >>>         print(f"Correlation: {corr_result.correlation:.3f}")
    >>>
    >>>     # Export for ML
    >>>     df = result.to_dataframe(lag_hours=5.5)
    >>>     df.to_csv('soyang_downstream_data.csv')
    >>>
    >>> asyncio.run(main())
"""

from kdm_sdk.templates import TemplateBuilder


def create_template():
    """소양강댐 하류 예측 템플릿 생성"""
    return (
        TemplateBuilder("소양강댐 하류 수위 예측")
        .description("소양강댐 방류량과 의암댐 수위의 상관관계 분석")
        .tags(["dam", "water_level", "correlation", "downstream"])
        .pair(
            upstream="소양강댐",
            downstream="의암댐",
            lag_hours=5.5,
            upstream_type="dam",
            downstream_type="water_level",
            upstream_items=["방류량"],
            downstream_items=["수위"],
        )
        .days(365)
        .time_key("h_1")
        .build()
    )


# Create template instance for direct import
template = create_template()


if __name__ == "__main__":
    import asyncio

    async def main():
        """Example execution"""
        print(f"Template: {template.name}")
        print(f"Description: {template.description}")
        print(f"Tags: {', '.join(template.tags)}")

        # Note: Requires KDM MCP server running
        # result = await template.execute()
        # df = result.to_dataframe(lag_hours=5.5)
        # print(f"Data shape: {df.shape}")

    asyncio.run(main())
