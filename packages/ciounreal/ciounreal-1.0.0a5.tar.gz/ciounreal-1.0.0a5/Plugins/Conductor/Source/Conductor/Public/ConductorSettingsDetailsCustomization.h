// Copyright 2024 CONDUCTOR TECHNOLOGIES. All Rights Reserved.

#pragma once

#include "ConductorCollectionPropertyDetailBuilder.h"
#include "IDetailChildrenBuilder.h"
#include "IDetailCustomization.h"
#include "IPropertyTypeCustomization.h"
#include "PropertyCustomizationHelpers.h"

class FDetailArrayBuilder;
// class FConductorDetailArrayBuilder;
class IDetailPropertyRow;
class UConductorMoviePipelineExecutorJob;

class FPropertyAvailabilityHandler
{
	UConductorMoviePipelineExecutorJob* Job;
	TSet<FName> PropertiesDisabledInDataAsset;
public:
	FPropertyAvailabilityHandler(UConductorMoviePipelineExecutorJob* InJob);

	static UConductorMoviePipelineExecutorJob* GetOuterJob(TSharedRef<IPropertyHandle> StructHandle);
	void EnableInMovieRenderQueue(IDetailPropertyRow& PropertyRow) const;
	void DisableRowInDataAsset(const IDetailPropertyRow& PropertyRow);

	bool IsPropertyRowEnabledInMovieRenderJob(const FName& InPropertyPath);
	bool IsPropertyRowEnabledInDataAsset(const FName& InPropertyPath);
};

class FConductorJobSettingsDetailsCustomization : public IPropertyTypeCustomization
{
public:

	static TSharedRef<IPropertyTypeCustomization> MakeInstance();

	/** Begin IPropertyTypeCustomization interface */
	virtual void CustomizeHeader(TSharedRef<IPropertyHandle> PropertyHandle, FDetailWidgetRow& HeaderRow, IPropertyTypeCustomizationUtils& CustomizationUtils) override;
	virtual void CustomizeChildren(TSharedRef<IPropertyHandle> StructHandle, IDetailChildrenBuilder& ChildBuilder, IPropertyTypeCustomizationUtils& CustomizationUtils) override;
	/** End IPropertyTypeCustomization interface */

protected:
	void CustomizeStructChildrenInAssetDetails(IDetailPropertyRow& PropertyRow) const;
	void CustomizeStructChildrenInMovieRenderQueue(IDetailPropertyRow& PropertyRow, UConductorMoviePipelineExecutorJob* Job) const;

	TSharedPtr<FPropertyAvailabilityHandler> PropertyOverrideHandler;
};


template<typename T>
class FConductorCollectionPropertyCustomization : public IPropertyTypeCustomization
{
public:

	/** Creates property customization instance */
	static TSharedRef<IPropertyTypeCustomization> MakeInstance()
	{
		return MakeShared<FConductorCollectionPropertyCustomization>();
	}

	FConductorCollectionPropertyCustomization() {}
	
	/** Begin IPropertyTypeCustomization interface */
	virtual void CustomizeHeader(
		TSharedRef<IPropertyHandle> InPropertyHandle,
		FDetailWidgetRow& InHeaderRow,
		IPropertyTypeCustomizationUtils& InCustomizationUtils) override;

	virtual void CustomizeChildren(
		TSharedRef<IPropertyHandle> InPropertyHandle,
		IDetailChildrenBuilder& InChildBuilder,
		IPropertyTypeCustomizationUtils& InCustomizationUtils) override;
	/** End IPropertyTypeCustomization interface */
	
private:
	// FConductorDetailArrayBuilder
	TSharedPtr<T> ArrayBuilder;
	TSharedPtr<FPropertyAvailabilityHandler> PropertyOverrideHandler;
};

template <typename T>
void FConductorCollectionPropertyCustomization<T>::CustomizeHeader(
	TSharedRef<IPropertyHandle> InPropertyHandle,
	FDetailWidgetRow& InHeaderRow,
	IPropertyTypeCustomizationUtils& InCustomizationUtils)
{
	// TODO Bad design. Now we assume that the first child property is a collection (map, array)
	const TSharedPtr<IPropertyHandle> ArrayHandle = InPropertyHandle->GetChildHandle(0);

	UConductorMoviePipelineExecutorJob* OuterJob = FPropertyAvailabilityHandler::GetOuterJob(InPropertyHandle);
	PropertyOverrideHandler = MakeShared<FPropertyAvailabilityHandler>(OuterJob);

	const FName PropertyPath = *InPropertyHandle->GetProperty()->GetPathName();

	ArrayBuilder = MakeShared<T>(ArrayHandle.ToSharedRef());
	if (PropertyOverrideHandler->GetOuterJob(InPropertyHandle))
	{
		ArrayBuilder->OnIsEnabled.BindLambda([this, PropertyPath]()
		{
			return this->PropertyOverrideHandler->IsPropertyRowEnabledInMovieRenderJob(PropertyPath);
		});
	}
	else
	{
		ArrayBuilder->OnIsEnabled.BindLambda([this, PropertyPath]()
		{
			return this->PropertyOverrideHandler->IsPropertyRowEnabledInDataAsset(PropertyPath);
		});
	}
	ArrayBuilder->GenerateWrapperStructHeaderRowContent(InHeaderRow, InPropertyHandle->CreatePropertyNameWidget());
}


template<typename T>
void FConductorCollectionPropertyCustomization<T>::CustomizeChildren(
	TSharedRef<IPropertyHandle> InPropertyHandle,
	IDetailChildrenBuilder& InChildBuilder,
	IPropertyTypeCustomizationUtils& InCustomizationUtils)
{
	InChildBuilder.AddCustomBuilder(ArrayBuilder.ToSharedRef());
}


class FConductorEnvValueDetailsCustomization : public IPropertyTypeCustomization
{
public:

	static TSharedRef<IPropertyTypeCustomization> MakeInstance();

	/** Begin IPropertyTypeCustomization interface */
	virtual void CustomizeHeader(TSharedRef<IPropertyHandle> PropertyHandle, FDetailWidgetRow& HeaderRow, IPropertyTypeCustomizationUtils& CustomizationUtils) override;
	virtual void CustomizeChildren(TSharedRef<IPropertyHandle> StructHandle, IDetailChildrenBuilder& ChildBuilder, IPropertyTypeCustomizationUtils& CustomizationUtils) override;
	/** End IPropertyTypeCustomization interface */
};

class FConductorPluginSettingsDetails : public IDetailCustomization
{
private:
	TWeakObjectPtr<UConductorPluginSettings> Settings;
public:
	/** Makes a new instance of this detail layout class for a specific detail view requesting it */
	static TSharedRef<IDetailCustomization> MakeInstance();
	// FText GetCredsState() const;

	/** IDetailCustomization interface */
	virtual void CustomizeDetails(IDetailLayoutBuilder& DetailBuilder) override;
};
