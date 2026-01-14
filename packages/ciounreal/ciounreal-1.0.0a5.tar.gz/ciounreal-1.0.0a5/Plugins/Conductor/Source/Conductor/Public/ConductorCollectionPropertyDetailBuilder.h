// Copyright 2024 CONDUCTOR TECHNOLOGIES. All Rights Reserved.

#pragma once
#include "IDetailChildrenBuilder.h"
#include "IDetailCustomNodeBuilder.h"
#include "PropertyCustomizationHelpers.h"
#include "ConductorSettings.h"

template<typename TCollectionPropertyHandle>
class FConductorCollectionPropertyDetailBuilder
	: public IDetailCustomNodeBuilder
{
public:

	FOnIsEnabled OnIsEnabled;
	
	void OnGenerateEntry(
		TSharedRef<IPropertyHandle> PropertyHandle,
		int32 ElementIndex,
		IDetailChildrenBuilder& ChildrenBuilder) const
	{
		this->GenerateEntry(PropertyHandle, ElementIndex, ChildrenBuilder);
	}

	FConductorCollectionPropertyDetailBuilder(
		TSharedRef<IPropertyHandle> InBaseProperty,
		bool InGenerateHeader = true,
		bool InDisplayResetToDefault = true,
		bool InDisplayElementNum = true
	) :
		  BaseProperty(InBaseProperty)
		, bGenerateHeader(InGenerateHeader)
		, bDisplayResetToDefault(InDisplayResetToDefault)
		, bDisplayElementNum(InDisplayElementNum)
	{
		BaseProperty->MarkHiddenByCustomization();
	}

	virtual ~FConductorCollectionPropertyDetailBuilder() override
	{
		// CollectionProperty->UnregisterOnNumElementsChanged(OnNumElementsChangedHandle);
	}

	void SetDisplayName(const FText& InDisplayName)
	{
		DisplayName = InDisplayName;
	}

	virtual bool RequiresTick() const override { return false; }

	virtual void Tick( float DeltaTime ) override {}

	virtual FName GetName() const override
	{
		return BaseProperty->GetProperty()->GetFName();
	}
	
	virtual bool InitiallyCollapsed() const override { return false; }

	void GenerateWrapperStructHeaderRowContent(FDetailWidgetRow& NodeRow, TSharedRef<SWidget> NameContent)
	{
		TSharedPtr<SHorizontalBox> ContentHorizontalBox;
		SAssignNew(ContentHorizontalBox, SHorizontalBox);
		if (bDisplayElementNum)
		{
			ContentHorizontalBox->AddSlot()
			[
				BaseProperty->CreatePropertyValueWidget()
			];
		}

		FUIAction CopyAction;
		FUIAction PasteAction;
		BaseProperty->CreateDefaultPropertyCopyPasteActions(CopyAction, PasteAction);

		NodeRow
		.FilterString(!DisplayName.IsEmpty() ? DisplayName : BaseProperty->GetPropertyDisplayName())
		.NameContent()
		[
			BaseProperty->CreatePropertyNameWidget(DisplayName, FText::GetEmpty())
		]
		.ValueContent()
		.HAlign( HAlign_Left )
		.VAlign( VAlign_Center )
		.MinDesiredWidth(170.f)
		.MaxDesiredWidth(170.f)
		[
			ContentHorizontalBox.ToSharedRef()
		]
		.CopyAction(CopyAction)
		.PasteAction(PasteAction);

		if (bDisplayResetToDefault)
		{
			TSharedPtr<SResetToDefaultMenu> ResetToDefaultMenu;
			ContentHorizontalBox->AddSlot()
			.AutoWidth()
			.Padding(FMargin(2.0f, 0.0f, 0.0f, 0.0f))
			[
				SAssignNew(ResetToDefaultMenu, SResetToDefaultMenu)
			];
			ResetToDefaultMenu->AddProperty(BaseProperty);
		}
		NodeRow.IsEnabled(TAttribute<bool>::CreateLambda([this]()
			{
				if (OnIsEnabled.IsBound())
					return OnIsEnabled.Execute();
				return true;
			})
		);

		NodeRow.ValueContent()
		.HAlign( HAlign_Left )
		.VAlign( VAlign_Center )
		.MinDesiredWidth(170.f)
		.MaxDesiredWidth(170.f);
		NodeRow.NameContent()
		[
			NameContent
		];
	}

	virtual void GenerateHeaderRowContent( FDetailWidgetRow& NodeRow ) override
	{
		// Do nothing
	}

	virtual void GenerateEntry(TSharedRef<IPropertyHandle> PropertyHandle, int32 ElementIndex,
													  IDetailChildrenBuilder& ChildrenBuilder) const
	{
		IDetailPropertyRow& PropertyRow = ChildrenBuilder.AddProperty(PropertyHandle);
		// Hide the reset to default button since it provides little value
		const FResetToDefaultOverride ResetDefaultOverride =
			FResetToDefaultOverride::Create(TAttribute<bool>(false));
	
		PropertyRow.OverrideResetToDefault(ResetDefaultOverride);
	
		TSharedPtr<SWidget> NameWidget;
		TSharedPtr<SWidget> ValueWidget;
		PropertyRow.GetDefaultWidgets( NameWidget, ValueWidget);
		PropertyRow.CustomWidget(false)
		.NameContent()
		.HAlign(HAlign_Fill)
		[
			NameWidget.ToSharedRef()
		]
		.ValueContent()
		.HAlign(HAlign_Fill)
		[
			ValueWidget.ToSharedRef()
		];
		PropertyRow.IsEnabled(TAttribute<bool>::CreateLambda([this]()
			{
				if (OnIsEnabled.IsBound())
					return OnIsEnabled.Execute();
				return true;
			}));
	}

	virtual void GenerateChildContent(IDetailChildrenBuilder& ChildrenBuilder) override
	{
		uint32 NumChildren = 0;
		CollectionProperty->GetNumElements(NumChildren);
		for( uint32 ChildIndex = 0; ChildIndex < NumChildren; ++ChildIndex)
		{
			const auto ElementHandle = BaseProperty->GetChildHandle(ChildIndex).ToSharedRef();
			GenerateEntry(ElementHandle, ChildIndex, ChildrenBuilder);
		}
	}

	virtual void RefreshChildren()
	{
		auto _ = OnRebuildChildren.ExecuteIfBound();
	}

	virtual TSharedPtr<IPropertyHandle> GetPropertyHandle() const override
	{
		return BaseProperty;
	}

protected:

	virtual void SetOnRebuildChildren( FSimpleDelegate InOnRebuildChildren  ) override { OnRebuildChildren = InOnRebuildChildren; } 

	void OnNumChildrenChanged() const
	{
		auto _ = OnRebuildChildren.ExecuteIfBound();
	}

	FText DisplayName;
	TSharedPtr<TCollectionPropertyHandle> CollectionProperty;
	TSharedRef<IPropertyHandle> BaseProperty;
	FSimpleDelegate OnRebuildChildren;
	// FDelegateHandle OnNumElementsChangedHandle;

	bool bGenerateHeader;
	bool bDisplayResetToDefault;
	bool bDisplayElementNum;
};

class FConductorFilesPropertyDetailBuilder : public FConductorCollectionPropertyDetailBuilder<IPropertyHandleArray>
{
public:
	FConductorFilesPropertyDetailBuilder(
		TSharedRef<IPropertyHandle> InBaseProperty,
		bool InGenerateHeader = true,
		bool InDisplayResetToDefault = true,
		bool InDisplayElementNum = true
	) : FConductorCollectionPropertyDetailBuilder(
		InBaseProperty, InGenerateHeader, InDisplayResetToDefault, InDisplayElementNum
	)
	{
		CollectionProperty = BaseProperty->AsArray();
		auto OnNumChildrenChanged = FSimpleDelegate::CreateRaw(
			this, &FConductorFilesPropertyDetailBuilder::OnNumChildrenChanged
		);
		
		/*OnNumElementsChangedHandle =*/ CollectionProperty->SetOnNumElementsChanged(
			OnNumChildrenChanged
		);
	}
};


class FConductorEnvValuePropertyDetailBuilder : public FConductorCollectionPropertyDetailBuilder<IPropertyHandleMap>
{
public:
	FConductorEnvValuePropertyDetailBuilder(
		TSharedRef<IPropertyHandle> InBaseProperty,
		bool InGenerateHeader = true,
		bool InDisplayResetToDefault = true,
		bool InDisplayElementNum = true
	) : FConductorCollectionPropertyDetailBuilder(
			InBaseProperty, InGenerateHeader, InDisplayResetToDefault, InDisplayElementNum
		)
	{
		CollectionProperty = BaseProperty->AsMap();
		// TODO Code duplication
		auto OnNumChildrenChanged = FSimpleDelegate::CreateRaw(
			this, &FConductorEnvValuePropertyDetailBuilder::OnNumChildrenChanged
		);
		/*OnNumElementsChangedHandle =*/ CollectionProperty->SetOnNumElementsChanged(
			OnNumChildrenChanged
		);
	}

protected:
	virtual void GenerateEntry(TSharedRef<IPropertyHandle> PropertyHandle, int32 ElementIndex, IDetailChildrenBuilder& ChildrenBuilder) const override
	{
		IDetailPropertyRow& PropertyRow = ChildrenBuilder.AddProperty(PropertyHandle);

		const auto ValueHandle = PropertyHandle->GetChildHandle(
			GET_MEMBER_NAME_CHECKED(FConductorEnvValue, Value)
		);
		const auto MergePolicyHandle = PropertyHandle->GetChildHandle(
			GET_MEMBER_NAME_CHECKED(FConductorEnvValue, MergePolicy)
		);
		
		const FResetToDefaultOverride ResetDefaultOverride =
			FResetToDefaultOverride::Create(TAttribute<bool>(false));
	
		PropertyRow.OverrideResetToDefault(ResetDefaultOverride);
	
		TSharedPtr<SWidget> NameWidget;
		TSharedPtr<SWidget> _;
		PropertyRow.GetDefaultWidgets( NameWidget, _);
		PropertyRow.CustomWidget(false)
		.NameContent()
		.HAlign(HAlign_Fill)
		[
			NameWidget.ToSharedRef()
		]
		.ValueContent()
		.HAlign(HAlign_Fill)
		[
			SNew(SHorizontalBox)
			+SHorizontalBox::Slot()
			.VAlign(VAlign_Center)
			.FillWidth(1.0f)
			.Padding(0.0f, 0.0f, 4.0f, 0.0f)
			[
				ValueHandle->CreatePropertyValueWidget()
			]
			+SHorizontalBox::Slot()
			.VAlign(VAlign_Center)
			.AutoWidth()
			.Padding(0.0f, 0.0f, 4.0f, 0.0f)
			[
				SNew(SBox)
				.MinDesiredHeight(24.f)
				.MinDesiredWidth(80.f)
				[
					MergePolicyHandle->CreatePropertyValueWidget()
				]
			]
		];
		PropertyRow.IsEnabled(TAttribute<bool>::CreateLambda([this]()
			{
				if (OnIsEnabled.IsBound())
					return OnIsEnabled.Execute();
				return true;
			}));
	}
};
