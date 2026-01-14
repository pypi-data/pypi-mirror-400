// Copyright 2024 CONDUCTOR TECHNOLOGIES. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "ConductorSettingsLibrary.generated.h"


/**
 * 
 */
UCLASS()
class CONDUCTOR_API UConductorSettingsLibrary : public UObject
{
	GENERATED_BODY()
public:
	static UConductorSettingsLibrary* Get();

	UFUNCTION(BlueprintImplementableEvent)
	FString GetJobTitle();

	UFUNCTION(BlueprintImplementableEvent)
	TArray<FString> GetProjects();

	UFUNCTION(BlueprintImplementableEvent)
	TArray<FString> GetInstanceTypes();

	UFUNCTION(BlueprintImplementableEvent)
	TArray<FString> GetEnvMergePolicy();

	UFUNCTION(BlueprintImplementableEvent)
	FString GetDefaultTaskTemplate();

	UFUNCTION(BlueprintImplementableEvent)
	FString GetPerforceServer();

	UFUNCTION(BlueprintImplementableEvent)
	FString GetPerforceUsername();

	UFUNCTION(BlueprintImplementableEvent)
	FString GetPerforcePassword();

	UFUNCTION(BlueprintImplementableEvent)
	void Reconnect();
	
};

