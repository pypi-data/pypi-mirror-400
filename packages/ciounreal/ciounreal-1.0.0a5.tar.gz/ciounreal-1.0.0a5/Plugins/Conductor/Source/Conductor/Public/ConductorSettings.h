// Copyright 2024 CONDUCTOR TECHNOLOGIES. All Rights Reserved.

#pragma once

#include "Engine/DataAsset.h"
#include "ConductorSettings.generated.h"


USTRUCT(BlueprintType)
struct CONDUCTOR_API FConductorFilesArray
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Uploads", meta=(RelativeToGameDir))
	TArray<FFilePath> Paths;
};

USTRUCT(BlueprintType)
struct CONDUCTOR_API FConductorDirectoriesArray
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Uploads", meta=(RelativeToGameDir))
	TArray<FDirectoryPath> Paths;
};

USTRUCT(BlueprintType)
struct CONDUCTOR_API FConductorEnvValue
{
	GENERATED_BODY()
	
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Environment")
	FString Value;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Environment", meta=(GetOptions="GetEnvMergePolicy"))
	FString MergePolicy;
};

USTRUCT(BlueprintType)
struct CONDUCTOR_API FConductorStringsMap
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Environment")
	TMap<FString, FConductorEnvValue> KeyValues;
};

USTRUCT(BlueprintType)
struct CONDUCTOR_API FConductorGeneralSettingsStruct
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "General Project", meta=(DisplayPriority=0))
	FString JobTitle;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "General Project", meta=(DisplayPriority=1, GetOptions="GetProjects"))
	FString Project;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "General Project", meta=(DisplayPriority=2, GetOptions="GetInstanceTypes"))
	FString InstanceType;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "General Project", meta=(DisplayPriority=3))
	bool bPreEmptible = false;

};

USTRUCT(BlueprintType)
struct CONDUCTOR_API FConductorUploadsSettingsStruct
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Upload", meta=(DisplayPriority=0))
	bool bUseDaemon = false;
	
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Upload", meta=(DisplayPriority=1))
	FConductorFilesArray Files;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Upload", meta=(DisplayPriority=2))
	FConductorDirectoriesArray Folders;
};

USTRUCT(BlueprintType)
struct CONDUCTOR_API FConductorEnvironmentSettingsStruct
{
	GENERATED_BODY()

	// TODO Slava rename
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Environment", meta=(DisplayPriority=0))
	FConductorStringsMap Variables;
};

USTRUCT(BlueprintType)
struct CONDUCTOR_API FConductorAdvancedSettingsStruct
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Advanced", meta=(DisplayPriority=0))
	FString Template;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Advanced", meta=(DisplayPriority=1))
	FString Notify;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Advanced", meta=(DisplayPriority=2))
	FString LocationTag;
};

USTRUCT(BlueprintType)
struct CONDUCTOR_API FConductorPerforceSettingsStruct
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Perforce", meta=(DisplayPriority=0))
	bool bUsePerforce = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Perforce", meta=(DisplayPriority=1, EditCondition="bUsePerforce", EditConditionHides))
	FString PerforceServer;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Perforce", meta=(DisplayPriority=2, EditCondition="bUsePerforce", EditConditionHides))
	FString PerforceUsername;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Perforce", meta=(DisplayPriority=3, EditCondition="bUsePerforce", EditConditionHides))
	FString PerforcePassword;

	UPROPERTY(VisibleAnywhere, Category = "Perforce", meta=(DisplayPriority=4, DisplayName="Notice", EditCondition="bUsePerforce", EditConditionHides))
	FString PerforceNotice = "Note that access to your Perforce server from Conductor's render nodes is required,\notherwise the render job will"
		" fail and it will still incur some compute costs. This may\nmean ensuring Conductor's IP ranges have been added to your Perforce"
		" server's\nIP allow list, and confirming your credentials are accurate.";
	
};

USTRUCT(BlueprintType)
struct CONDUCTOR_API FConductorSettingsStruct
{
	GENERATED_BODY()

	/** Job shared settings */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Job Settings")
	FConductorGeneralSettingsStruct GeneralSettings;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Job Settings")
	FConductorUploadsSettingsStruct UploadsSettings;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Job Settings")
	FConductorEnvironmentSettingsStruct EnvironmentSettings;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Job Settings")
	FConductorAdvancedSettingsStruct AdvancedSettings;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Job Settings")
	FConductorPerforceSettingsStruct PerforceSettings;
	
};


/**
 * Conductor job settings may
 */
UCLASS(BlueprintType)
class CONDUCTOR_API UConductorSettings : public UDataAsset
{
	GENERATED_BODY()

public:
	/** Conductor job settings container struct */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Job Settings")
	FConductorSettingsStruct SettingsContainer;
public:

	UConductorSettings();
	
	/** Python exposed option lists */
	UFUNCTION()
	TArray<FString> GetProjects();

	UFUNCTION()
	TArray<FString> GetInstanceTypes();

	UFUNCTION()
	TArray<FString> GetEnvMergePolicy();

};

/**
 * 
 */
UCLASS(BlueprintType, Config = Editor, DefaultConfig)
class CONDUCTOR_API UConductorPluginSettings : public UDeveloperSettings
{
	GENERATED_BODY()

public:

	/** @return Plugin settings main menu option */
	virtual FName GetContainerName() const override { return FName("Project"); }
	
	/** @return Plugin settings category */
	virtual FName GetCategoryName() const override { return FName("Plugins"); }

#if WITH_EDITOR
	virtual FText GetSectionText() const override;
	virtual FName GetSectionName() const override;
#endif
	UConductorPluginSettings();

};
