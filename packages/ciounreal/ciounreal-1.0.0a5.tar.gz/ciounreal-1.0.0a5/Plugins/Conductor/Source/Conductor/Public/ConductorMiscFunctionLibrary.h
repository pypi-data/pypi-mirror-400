// Copyright 2024 CONDUCTOR TECHNOLOGIES. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "ConductorMiscFunctionLibrary.generated.h"

/**
 * 
 */
UCLASS(BlueprintType)
class CONDUCTOR_API UConductorMiscFunctionLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

	UFUNCTION(BlueprintCallable, Category=Conductor)
	static void RequestExit(bool bForce, int32 ExitCode);
};
