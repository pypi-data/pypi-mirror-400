#include "ConductorStyle.h"

#include "Styling/SlateStyleRegistry.h"

#define IMAGE_BRUSH(RelativePath, ...) FSlateImageBrush(StyleSet->RootToContentDir(RelativePath, TEXT(".png")), __VA_ARGS__)

void FConductorStyle::Initialize()
{
	const FVector2D Icon16x16(16.0f, 16.0f);
	const FVector2D Icon20x20(20.0f, 20.0f);
	const FVector2D Icon40x40(40.0f, 40.0f);
	const FVector2D Icon128x128(128.0f, 128.0f);

	if (StyleSet.IsValid())
	{
		return;
	}

	const auto ResourcePath = FPaths::ProjectPluginsDir() / TEXT("Conductor/Resources");
	StyleSet = MakeUnique<FSlateStyleSet>(GetStyleSetName());
	StyleSet->SetContentRoot(ResourcePath);
	UE_LOG(LogTemp, Log, TEXT("Current resource path: %s"), *ResourcePath);
	{
		StyleSet->Set("Conductor.Icon.Context", new IMAGE_BRUSH("Icon16", Icon16x16));
		StyleSet->Set("Conductor.Icon.Small", new IMAGE_BRUSH("Icon20", Icon20x20));
		StyleSet->Set("Conductor.Icon", new IMAGE_BRUSH("Icon40", Icon40x40));
		StyleSet->Set("Conductor.Icon.Plugin", new IMAGE_BRUSH("Icon128", Icon40x40));
	}

	FSlateStyleRegistry::RegisterSlateStyle(*StyleSet.Get());
}

void FConductorStyle::Shutdown()
{
	if (StyleSet.IsValid())
	{
		FSlateStyleRegistry::UnRegisterSlateStyle(*StyleSet.Get());
		StyleSet.Reset();
	}
}

TUniquePtr<FSlateStyleSet> FConductorStyle::StyleSet = nullptr;

const ISlateStyle& FConductorStyle::Get()
{
	check(StyleSet);
	return *StyleSet;
}

FName FConductorStyle::GetStyleSetName()
{
	static FName StyleSetName(TEXT("ConductorStyle"));
	return StyleSetName;
}
