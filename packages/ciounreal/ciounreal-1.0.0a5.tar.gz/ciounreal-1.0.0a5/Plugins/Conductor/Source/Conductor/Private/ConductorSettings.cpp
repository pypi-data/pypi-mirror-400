// Copyright 2024 CONDUCTOR TECHNOLOGIES. All Rights Reserved.


#include "ConductorSettings.h"

#include "ConductorSettingsLibrary.h"

UConductorSettings::UConductorSettings()
{
	if (UConductorSettingsLibrary::Get())
	{
		SettingsContainer.GeneralSettings.JobTitle = UConductorSettingsLibrary::Get()->GetJobTitle();
		SettingsContainer.AdvancedSettings.Template = UConductorSettingsLibrary::Get()->GetDefaultTaskTemplate();
		SettingsContainer.PerforceSettings.PerforceServer = UConductorSettingsLibrary::Get()->GetPerforceServer();
		SettingsContainer.PerforceSettings.PerforceUsername = UConductorSettingsLibrary::Get()->GetPerforceUsername();
		SettingsContainer.PerforceSettings.PerforcePassword = UConductorSettingsLibrary::Get()->GetPerforcePassword();
	}
}

TArray<FString> UConductorSettings::GetProjects()
{
	return UConductorSettingsLibrary::Get()->GetProjects();
}

TArray<FString> UConductorSettings::GetInstanceTypes()
{
	return UConductorSettingsLibrary::Get()->GetInstanceTypes();
}

TArray<FString> UConductorSettings::GetEnvMergePolicy()
{
	return UConductorSettingsLibrary::Get()->GetEnvMergePolicy();
}

FText UConductorPluginSettings::GetSectionText() const
{
	return NSLOCTEXT("ConductorPluginSettings", "ConductorPluginSettingsSection", "Conductor");
}

FName UConductorPluginSettings::GetSectionName() const
{
	return TEXT("Conductor");
}

UConductorPluginSettings::UConductorPluginSettings()
{
}

