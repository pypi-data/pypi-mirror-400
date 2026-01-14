// Copyright 2024 CONDUCTOR TECHNOLOGIES. All Rights Reserved.

#include "ConductorMiscFunctionLibrary.h"

void UConductorMiscFunctionLibrary::RequestExit(const bool bForce, const int32 ExitCode)
{
	FPlatformMisc::RequestExitWithStatus(bForce, ExitCode);
}
