// Copyright 2024 CONDUCTOR TECHNOLOGIES. All Rights Reserved.

#include "ConductorSettingsLibrary.h"

UConductorSettingsLibrary* UConductorSettingsLibrary::Get()
{
	TArray<UClass*> PythonAPIClasses;
	GetDerivedClasses(UConductorSettingsLibrary::StaticClass(), PythonAPIClasses);
	if (PythonAPIClasses.Num() > 0)
	{
		return Cast<UConductorSettingsLibrary>(PythonAPIClasses[PythonAPIClasses.Num() - 1]->GetDefaultObject());
	}
	return nullptr;
}
