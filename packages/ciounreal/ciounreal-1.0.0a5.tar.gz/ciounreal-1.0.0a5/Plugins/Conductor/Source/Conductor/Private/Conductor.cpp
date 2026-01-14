// Copyright 2024 CONDUCTOR TECHNOLOGIES. All Rights Reserved.

#include "Conductor.h"
#include "ConductorMoviePipelineExecutorJob.h"
#include "ConductorSettingsDetailsCustomization.h"
#include "ConductorStyle.h"

#define LOCTEXT_NAMESPACE "FConductorModule"

void FConductorModule::StartupModule()
{
	FConductorStyle::Initialize();

	FPropertyEditorModule& PropertyModule = FModuleManager::GetModuleChecked<FPropertyEditorModule>("PropertyEditor");

	// Plugins settings
	PropertyModule.RegisterCustomClassLayout(
		UConductorPluginSettings::StaticClass()->GetFName(),
		FOnGetDetailCustomizationInstance::CreateStatic(&FConductorPluginSettingsDetails::MakeInstance)
	);

	// MRQ Job details
	PropertyModule.RegisterCustomClassLayout(
		UConductorMoviePipelineExecutorJob::StaticClass()->GetFName(),
		FOnGetDetailCustomizationInstance::CreateStatic(&FConductorMoviePipelineExecutorJobCustomization::MakeInstance)
	);

	// Settings details
	PropertyModule.RegisterCustomPropertyTypeLayout(
		FConductorGeneralSettingsStruct::StaticStruct()->GetFName(),
		FOnGetPropertyTypeCustomizationInstance::CreateStatic(
			&FConductorJobSettingsDetailsCustomization::MakeInstance)
	);
	PropertyModule.RegisterCustomPropertyTypeLayout(
		FConductorUploadsSettingsStruct::StaticStruct()->GetFName(),
		FOnGetPropertyTypeCustomizationInstance::CreateStatic(
			&FConductorJobSettingsDetailsCustomization::MakeInstance)
	);
	PropertyModule.RegisterCustomPropertyTypeLayout(
		FConductorEnvironmentSettingsStruct::StaticStruct()->GetFName(),
		FOnGetPropertyTypeCustomizationInstance::CreateStatic(
			&FConductorJobSettingsDetailsCustomization::MakeInstance)
	);
	PropertyModule.RegisterCustomPropertyTypeLayout(
		FConductorAdvancedSettingsStruct::StaticStruct()->GetFName(),
		FOnGetPropertyTypeCustomizationInstance::CreateStatic(
			&FConductorJobSettingsDetailsCustomization::MakeInstance)
	);
	PropertyModule.RegisterCustomPropertyTypeLayout(
		FConductorPerforceSettingsStruct::StaticStruct()->GetFName(),
		FOnGetPropertyTypeCustomizationInstance::CreateStatic(
			&FConductorJobSettingsDetailsCustomization::MakeInstance)
	);

	// Collections
	PropertyModule.RegisterCustomPropertyTypeLayout(
		FConductorFilesArray::StaticStruct()->GetFName(),
		FOnGetPropertyTypeCustomizationInstance::CreateStatic(
			&FConductorCollectionPropertyCustomization<FConductorFilesPropertyDetailBuilder>::MakeInstance)
	);
	PropertyModule.RegisterCustomPropertyTypeLayout(
		FConductorDirectoriesArray::StaticStruct()->GetFName(),
		FOnGetPropertyTypeCustomizationInstance::CreateStatic(
			&FConductorCollectionPropertyCustomization<FConductorFilesPropertyDetailBuilder>::MakeInstance)
	);
	PropertyModule.RegisterCustomPropertyTypeLayout(
		FConductorStringsMap::StaticStruct()->GetFName(),
		FOnGetPropertyTypeCustomizationInstance::CreateStatic(
			&FConductorCollectionPropertyCustomization<FConductorEnvValuePropertyDetailBuilder>::MakeInstance)
	);

	// Env variables
	PropertyModule.RegisterCustomPropertyTypeLayout(
		FConductorEnvValue::StaticStruct()->GetFName(),
		FOnGetPropertyTypeCustomizationInstance::CreateStatic(
			&FConductorEnvValueDetailsCustomization::MakeInstance)
	);
	
	PropertyModule.NotifyCustomizationModuleChanged();
}

void FConductorModule::ShutdownModule()
{
	// This function may be called during shutdown to clean up your module.  For modules that support dynamic reloading,
	// we call this function before unloading the module.
}

#undef LOCTEXT_NAMESPACE
	
IMPLEMENT_MODULE(FConductorModule, Conductor)