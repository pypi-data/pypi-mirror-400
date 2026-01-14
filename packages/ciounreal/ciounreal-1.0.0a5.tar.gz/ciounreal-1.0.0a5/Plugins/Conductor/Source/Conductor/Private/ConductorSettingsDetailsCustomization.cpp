// Copyright 2024 CONDUCTOR TECHNOLOGIES. All Rights Reserved.

#include "ConductorSettingsDetailsCustomization.h"
#include "ConductorMoviePipelineExecutorJob.h"
#include "ConductorSettingsLibrary.h"
#include "DetailLayoutBuilder.h"
#include "DetailWidgetRow.h"
#include "EditorStyleSet.h"
#include "IDetailChildrenBuilder.h"
#include "IDetailGroup.h"
#include "PropertyCustomizationHelpers.h"
#include "Widgets/Input/SCheckBox.h"
#include "Misc/EngineVersionComparison.h"

#define LOCTEXT_NAMESPACE "SConductorDetails"

// TODO Slava double check we need this
class SEyeCheckBox : public SCompoundWidget
{
public:
	SLATE_BEGIN_ARGS( SEyeCheckBox ){}

	SLATE_END_ARGS()
	
	void Construct(const FArguments& InArgs, const FName& InPropertyPath)
	{		
		ChildSlot
		[
			SNew(SBox)
			.Visibility(EVisibility::Visible)
			.HAlign(HAlign_Right)
			.WidthOverride(28)
			.HeightOverride(20)
#if UE_VERSION_NEWER_THAN(5, 1, -1)
			.Padding(4, 0)
#else
			.Padding(4)
#endif
			[
				SAssignNew(CheckBoxPtr, SCheckBox)
				.Style(&FAppStyle::Get().GetWidgetStyle<FCheckBoxStyle>("ToggleButtonCheckbox"))
				.Visibility_Lambda([this]()
				{
					return CheckBoxPtr.IsValid() && !CheckBoxPtr->IsChecked() ? EVisibility::Visible : IsHovered() ? EVisibility::Visible : EVisibility::Hidden;
				})
				.CheckedImage(FAppStyle::Get().GetBrush("Icons.Visible"))
				.CheckedHoveredImage(FAppStyle::Get().GetBrush("Icons.Visible"))
				.CheckedPressedImage(FAppStyle::Get().GetBrush("Icons.Visible"))
				.UncheckedImage(FAppStyle::Get().GetBrush("Icons.Hidden"))
				.UncheckedHoveredImage(FAppStyle::Get().GetBrush("Icons.Hidden"))
				.UncheckedPressedImage(FAppStyle::Get().GetBrush("Icons.Hidden"))
				.ToolTipText(NSLOCTEXT("FConductorJobPresetLibraryCustomization", "VisibleInMoveRenderQueueToolTip", "If true this property will be visible for overriding from Movie Render Queue."))
				.IsChecked_Lambda([InPropertyPath]()
				{
					// TODO Slava Double check
					return ECheckBoxState::Checked;
				})
			]
		];
	}

	TSharedPtr<SCheckBox> CheckBoxPtr;
};

TSharedRef<IPropertyTypeCustomization> FConductorJobSettingsDetailsCustomization::MakeInstance()
{
	return MakeShared<FConductorJobSettingsDetailsCustomization>();
}

void FConductorJobSettingsDetailsCustomization::CustomizeHeader(TSharedRef<IPropertyHandle> PropertyHandle, FDetailWidgetRow& HeaderRow,
	IPropertyTypeCustomizationUtils& CustomizationUtils)
{
}

void FConductorJobSettingsDetailsCustomization::CustomizeChildren(
	TSharedRef<IPropertyHandle> StructHandle,
    IDetailChildrenBuilder& ChildBuilder, IPropertyTypeCustomizationUtils& CustomizationUtils)
{
	UConductorMoviePipelineExecutorJob* OuterJob = FPropertyAvailabilityHandler::GetOuterJob(StructHandle);
	PropertyOverrideHandler = MakeShared<FPropertyAvailabilityHandler>(OuterJob);

	TMap<FName, IDetailGroup*> CreatedCategories;
	const FName StructName(StructHandle->GetProperty()->GetFName());

	if (OuterJob)
	{
		IDetailGroup& BaseCategoryGroup = ChildBuilder.AddGroup(StructName, StructHandle->GetPropertyDisplayName());
		CreatedCategories.Add(StructName, &BaseCategoryGroup);
	}
	
	// For each map member and each struct member in the map member value
	uint32 NumChildren;
	StructHandle->GetNumChildren(NumChildren);
	
	// For each struct member
	for (uint32 ChildIndex = 0; ChildIndex < NumChildren; ++ChildIndex)
	{
		const TSharedRef<IPropertyHandle> ChildHandle = StructHandle->GetChildHandle(ChildIndex).ToSharedRef();

		IDetailGroup* GroupToUse = nullptr;
		if (const FString* PropertyCategoryString = ChildHandle->GetProperty()->FindMetaData(TEXT("Category")))
		{
			FName PropertyCategoryName(*PropertyCategoryString);

			if (IDetailGroup** FoundCategory = CreatedCategories.Find(PropertyCategoryName))
			{
				GroupToUse = *FoundCategory;
			}
			else
			{
				if (OuterJob)
				{
					GroupToUse = CreatedCategories.FindChecked(StructName);
				}
				else
				{
					IDetailGroup& NewGroup = ChildBuilder.AddGroup(StructName, StructHandle->GetPropertyDisplayName());
					NewGroup.ToggleExpansion(true);
					GroupToUse = CreatedCategories.Add(PropertyCategoryName, &NewGroup);
				}
			}
		}
		
		IDetailPropertyRow& PropertyRow = GroupToUse->AddPropertyRow(ChildHandle);

		if (OuterJob)
		{
			CustomizeStructChildrenInMovieRenderQueue(PropertyRow, OuterJob);
		}
		else
		{
			CustomizeStructChildrenInAssetDetails(PropertyRow);
		}
	}

	// Force expansion of all categories
	for (const TTuple<FName, IDetailGroup*>& Pair : CreatedCategories)
	{
		if (Pair.Value)
		{
			Pair.Value->ToggleExpansion(true);
		}
	}
}

void FConductorJobSettingsDetailsCustomization::CustomizeStructChildrenInAssetDetails(
	IDetailPropertyRow& PropertyRow) const
{
	TSharedPtr<SWidget> NameWidget;
	TSharedPtr<SWidget> ValueWidget;
	FDetailWidgetRow Row;
	PropertyRow.GetDefaultWidgets(NameWidget, ValueWidget, Row);

	PropertyRow.CustomWidget(true)
	.NameContent()
	.MinDesiredWidth(Row.NameWidget.MinWidth)
	.MaxDesiredWidth(Row.NameWidget.MaxWidth)
	.HAlign(HAlign_Fill)
	[
		NameWidget.ToSharedRef()
	]
	.ValueContent()
	.MinDesiredWidth(Row.ValueWidget.MinWidth)
	.MaxDesiredWidth(Row.ValueWidget.MaxWidth)
	.VAlign(VAlign_Center)
	[
		ValueWidget.ToSharedRef()
	];
	/*
	.ExtensionContent()
	[
		SNew(SEyeCheckBox, *PropertyRow.GetPropertyHandle()->GetProperty()->GetPathName())
	];
	*/
}

void FConductorJobSettingsDetailsCustomization::CustomizeStructChildrenInMovieRenderQueue(
	IDetailPropertyRow& PropertyRow, UConductorMoviePipelineExecutorJob* Job) const
{
	PropertyOverrideHandler->EnableInMovieRenderQueue(PropertyRow);
}

TSharedRef<IPropertyTypeCustomization> FConductorEnvValueDetailsCustomization::MakeInstance()
{
	return MakeShared<FConductorEnvValueDetailsCustomization>();
}

void FConductorEnvValueDetailsCustomization::CustomizeHeader(TSharedRef<IPropertyHandle> PropertyHandle, FDetailWidgetRow& HeaderRow,
	IPropertyTypeCustomizationUtils& CustomizationUtils)
{
	
}

void FConductorEnvValueDetailsCustomization::CustomizeChildren(TSharedRef<IPropertyHandle> StructHandle, IDetailChildrenBuilder& ChildBuilder,
	IPropertyTypeCustomizationUtils& CustomizationUtils)
{
	const auto ValueHandle = StructHandle->GetChildHandle(0);
	const auto MergeTypeHandle = StructHandle->GetChildHandle(1);

	ChildBuilder
	.AddCustomRow(FText::GetEmpty())
	.WholeRowContent()
	[
		SNew(SHorizontalBox)
		+SHorizontalBox::Slot()
		.AutoWidth()
		.VAlign(VAlign_Center)
		.Padding(0.0f, 0.0f, 4.0f, 0.0f)
		[
			ValueHandle->CreatePropertyValueWidget()
		]
		+SHorizontalBox::Slot()
		.AutoWidth()
		.VAlign(VAlign_Center)
		.Padding(0.0f, 0.0f, 4.0f, 0.0f)
		[
			MergeTypeHandle->CreatePropertyValueWidget()
		]
	];
}

TSharedRef<IDetailCustomization> FConductorPluginSettingsDetails::MakeInstance()
{
	return MakeShareable(new FConductorPluginSettingsDetails);
}

void FConductorPluginSettingsDetails::CustomizeDetails(IDetailLayoutBuilder& DetailBuilder)
{
	TArray<TWeakObjectPtr<UObject>> ObjectsBeingCustomized;
	DetailBuilder.GetObjectsBeingCustomized(ObjectsBeingCustomized);
	Settings = Cast<UConductorPluginSettings>(ObjectsBeingCustomized[0].Get());

	IDetailCategoryBuilder& LoginCategory = DetailBuilder.EditCategory("Reconnect Conductor");
	LoginCategory.AddCustomRow(LOCTEXT("ConductorReconnect", "ConductorReconnect"))
		.ValueContent()
		[
			SNew(SHorizontalBox)
			+ SHorizontalBox::Slot()
			.Padding(FMargin(5, 5, 5, 5))
			.AutoWidth()
			[
				SNew(SButton)
				.Text(LOCTEXT("ConductorReconnect", "Reconnect"))
				.ToolTipText(LOCTEXT("ConductorReconnect_Tooltip", "Reconnect"))
				.OnClicked_Lambda([this]()
				{
					if (const auto ConductorLib = UConductorSettingsLibrary::Get())
					{
						ConductorLib->Reconnect();
					}
					return(FReply::Handled());
				})
			]
		];
}


FPropertyAvailabilityHandler::FPropertyAvailabilityHandler(UConductorMoviePipelineExecutorJob* InJob)
	: Job(InJob)
{
	
}

UConductorMoviePipelineExecutorJob* FPropertyAvailabilityHandler::GetOuterJob(TSharedRef<IPropertyHandle> StructHandle)
{
	TArray<UObject*> OuterObjects;
	StructHandle->GetOuterObjects(OuterObjects);

	if (OuterObjects.Num() == 0)
	{
		return nullptr;
	}

	const TWeakObjectPtr<UObject> OuterObject = OuterObjects[0];
	if (!OuterObject.IsValid())
	{
		return nullptr;
	}
	UConductorMoviePipelineExecutorJob* OuterJob = Cast<UConductorMoviePipelineExecutorJob>(OuterObject);
	return OuterJob;
}

bool FPropertyAvailabilityHandler::IsPropertyRowEnabledInMovieRenderJob(const FName& InPropertyPath)
{
	return Job && Job->IsPropertyRowEnabledInMovieRenderJob(InPropertyPath);
}

bool FPropertyAvailabilityHandler::IsPropertyRowEnabledInDataAsset(const FName& InPropertyPath)
{
	if (PropertiesDisabledInDataAsset.Contains(InPropertyPath))
	{
		return false;
	}
	return true;
}

void FPropertyAvailabilityHandler::DisableRowInDataAsset(const IDetailPropertyRow& PropertyRow)
{
	const FName PropertyPath = *PropertyRow.GetPropertyHandle()->GetProperty()->GetPathName();
	PropertiesDisabledInDataAsset.Add(PropertyPath);
}


void FPropertyAvailabilityHandler::EnableInMovieRenderQueue(IDetailPropertyRow& PropertyRow) const
{
	if (!Job) return;
	
	TSharedPtr<SWidget> NameWidget;
	TSharedPtr<SWidget> ValueWidget;
	FDetailWidgetRow Row;
	PropertyRow.GetDefaultWidgets(NameWidget, ValueWidget, Row);
	
	const FName PropertyPath = *PropertyRow.GetPropertyHandle()->GetProperty()->GetPathName();
	ValueWidget->SetEnabled(
		TAttribute<bool>::CreateLambda([this, PropertyPath]()
			{
				return Job->IsPropertyRowEnabledInMovieRenderJob(PropertyPath); 
			}
		)
	);

	PropertyRow
	.OverrideResetToDefault(FResetToDefaultOverride::Hide())
	.CustomWidget(true)
	.NameContent()
	.MinDesiredWidth(Row.NameWidget.MinWidth)
	.MaxDesiredWidth(Row.NameWidget.MaxWidth)
	.HAlign(HAlign_Fill)
	[
		SNew(SHorizontalBox)
		+ SHorizontalBox::Slot()
		.AutoWidth()
		.Padding(4, 0)
		[
			SNew(SCheckBox)
			.IsChecked_Lambda([this, PropertyPath]()
			{
				return Job->IsPropertyRowEnabledInMovieRenderJob(PropertyPath) ?
					ECheckBoxState::Checked : ECheckBoxState::Unchecked; 
			})
			.OnCheckStateChanged_Lambda([this, PropertyPath](const ECheckBoxState NewState)
			{
				return Job->SetPropertyRowEnabledInMovieRenderJob(
					PropertyPath, NewState == ECheckBoxState::Checked
				); 
			})
		]
		+ SHorizontalBox::Slot()
		[
			NameWidget.ToSharedRef()
		]
	]
	.ValueContent()
	.MinDesiredWidth(Row.ValueWidget.MinWidth)
	.MaxDesiredWidth(Row.ValueWidget.MaxWidth)
	.VAlign(VAlign_Center)
	[
		ValueWidget.ToSharedRef()
	];
}
