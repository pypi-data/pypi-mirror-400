// Copyright 2024 CONDUCTOR TECHNOLOGIES. All Rights Reserved.


#include "ConductorMoviePipelineExecutorJob.h"

#include "ConductorSettingsLibrary.h"
#include "DetailCategoryBuilder.h"
#include "DetailLayoutBuilder.h"


UConductorMoviePipelineExecutorJob::UConductorMoviePipelineExecutorJob()
{
	if (UConductorSettingsLibrary::Get())
	{
		ConductorSettings.GeneralSettings.JobTitle = UConductorSettingsLibrary::Get()->GetJobTitle();
		ConductorSettings.AdvancedSettings.Template = UConductorSettingsLibrary::Get()->GetDefaultTaskTemplate();
	}
}

bool UConductorMoviePipelineExecutorJob::IsPropertyRowEnabledInMovieRenderJob(const FName& InPropertyPath) const
{
	if (const FPropertyRowEnabledInfo* Match = Algo::FindByPredicate(
		EnabledPropertyOverrides,
		[&InPropertyPath](const FPropertyRowEnabledInfo& Info) { return Info.PropertyPath == InPropertyPath; }
	))
	{
		return Match->bIsEnabled;
	}
	return false;
}

void UConductorMoviePipelineExecutorJob::SetPropertyRowEnabledInMovieRenderJob(const FName& InPropertyPath, bool bInEnabled)
{
	if (FPropertyRowEnabledInfo* Match = Algo::FindByPredicate(EnabledPropertyOverrides,
	 [&InPropertyPath](const FPropertyRowEnabledInfo& Info)
	 {
		 return Info.PropertyPath == InPropertyPath;
	 }))
	{
		Match->bIsEnabled = bInEnabled;
	}
	else
	{
		EnabledPropertyOverrides.Add({InPropertyPath, bInEnabled});
	}
}

void UConductorMoviePipelineExecutorJob::PostEditChangeProperty(FPropertyChangedEvent& PropertyChangedEvent)
{
	// Check if we changed the job Preset an update the override details
	if (const FName PropertyName = PropertyChangedEvent.GetPropertyName(); PropertyName == "JobSettings")
	{
		if (const UConductorSettings* SelectedJobSettings = JobSettings)
		{
			// TODO Slava use reflection, double check this works
			ConductorSettings.GeneralSettings = SelectedJobSettings->SettingsContainer.GeneralSettings;
			ConductorSettings.UploadsSettings = SelectedJobSettings->SettingsContainer.UploadsSettings;
			ConductorSettings.EnvironmentSettings = SelectedJobSettings->SettingsContainer.EnvironmentSettings;
			ConductorSettings.AdvancedSettings = SelectedJobSettings->SettingsContainer.AdvancedSettings;
			ConductorSettings.PerforceSettings = SelectedJobSettings->SettingsContainer.PerforceSettings;
		}
	}
}

void UConductorMoviePipelineExecutorJob::PostEditChangeChainProperty(FPropertyChangedChainEvent& PropertyChangedEvent)
{
	Super::PostEditChangeChainProperty(PropertyChangedEvent);
}

TArray<FString> UConductorMoviePipelineExecutorJob::GetProjects()
{
	return UConductorSettingsLibrary::Get()->GetProjects();
}

TArray<FString> UConductorMoviePipelineExecutorJob::GetInstanceTypes()
{
	return UConductorSettingsLibrary::Get()->GetInstanceTypes();
}

TArray<FString> UConductorMoviePipelineExecutorJob::GetEnvMergePolicy()
{
	return UConductorSettingsLibrary::Get()->GetEnvMergePolicy();
}

TSharedRef<IDetailCustomization> FConductorMoviePipelineExecutorJobCustomization::MakeInstance()
{
	return MakeShared<FConductorMoviePipelineExecutorJobCustomization>();
}

// TODO Slava remove this probably
void FConductorMoviePipelineExecutorJobCustomization::CustomizeDetails(IDetailLayoutBuilder& DetailBuilder)
{
	IDetailCategoryBuilder& MrpCategory = DetailBuilder.EditCategory("Movie Render Pipeline");

	TArray<TSharedRef<IPropertyHandle>> OutMrpCategoryProperties;
	MrpCategory.GetDefaultProperties(OutMrpCategoryProperties);

	// We hide these properties because we want to use "Name", "UserName" and "Comment" from the Conductor preset
	const TArray<FName> PropertiesToHide = {"JobName", "Author", "Comment"};

	for (const TSharedRef<IPropertyHandle>& PropertyHandle : OutMrpCategoryProperties)
	{
		if (PropertiesToHide.Contains(PropertyHandle->GetProperty()->GetFName()))
		{
			PropertyHandle->MarkHiddenByCustomization();
		}
	}
}
