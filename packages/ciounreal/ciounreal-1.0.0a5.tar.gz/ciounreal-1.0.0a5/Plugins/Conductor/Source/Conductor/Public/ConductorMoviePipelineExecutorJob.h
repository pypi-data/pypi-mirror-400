// Copyright 2024 CONDUCTOR TECHNOLOGIES. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "ConductorSettings.h"
#include "IDetailCustomization.h"
#include "MoviePipelineQueue.h"

#include "ConductorMoviePipelineExecutorJob.generated.h"

/**
 * Helper struct, contains property row checkbox state
 */
USTRUCT()
struct FPropertyRowEnabledInfo
{
	GENERATED_BODY()
	
	FName PropertyPath;
	bool bIsEnabled = false;
};

UCLASS(BlueprintType, config = EditorPerProjectUserSettings)
class CONDUCTOR_API UConductorMoviePipelineExecutorJob : public UMoviePipelineExecutorJob
{
	GENERATED_BODY()

public:

	UConductorMoviePipelineExecutorJob();

	bool IsPropertyRowEnabledInMovieRenderJob(const FName& InPropertyPath) const;
	void SetPropertyRowEnabledInMovieRenderJob(const FName& InPropertyPath, bool bInEnabled);

	// UFUNCTION(BlueprintCallable)
	// FConductorSettingsStruct GetResultingConductorSettings() const;

#if WITH_EDITOR
	virtual void PostEditChangeProperty(FPropertyChangedEvent& PropertyChangedEvent) override;
	virtual void PostEditChangeChainProperty(FPropertyChangedChainEvent& PropertyChangedEvent) override;
#endif

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Conductor Settings")
	TObjectPtr<UConductorSettings> JobSettings;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, config, Category = "Overrides")
	FConductorSettingsStruct ConductorSettings = FConductorSettingsStruct();
	
protected:

	// void GetStructWithOverrides(const UStruct* InStruct, const void* InContainer, void* OutContainer) const;

	UPROPERTY(config)
	TArray<FPropertyRowEnabledInfo> EnabledPropertyOverrides;
public:
	/** Python exposed settings */
	UFUNCTION()
	TArray<FString> GetProjects();

	UFUNCTION()
	TArray<FString> GetInstanceTypes();

	UFUNCTION()
	TArray<FString> GetEnvMergePolicy();
};

class FConductorMoviePipelineExecutorJobCustomization : public IDetailCustomization
{
public:

	static TSharedRef<IDetailCustomization> MakeInstance();

	/** Begin IDetailCustomization interface */
	virtual void CustomizeDetails(IDetailLayoutBuilder& DetailBuilder) override;
	/** End IDetailCustomization interface */
};
