// Copyright 2024 CONDUCTOR TECHNOLOGIES. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Styling/ISlateStyle.h"
#include "Styling/SlateStyle.h"

class FConductorStyle
{
public:
	static void Initialize();
	static void Shutdown();

	static const ISlateStyle& Get();

	static FName GetStyleSetName();

private:
	static TUniquePtr<FSlateStyleSet> StyleSet;
};
