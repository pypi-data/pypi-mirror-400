from enum import Enum

# Used by
#	AttributeDefinitionInterface.Get
#	AttributeDefinitionInterface.Set
#	AttributeDefinitionInterface.Create
#	AttributeDefinitionInterface.GetFromDatabase
class AD_Direction(Enum):
    LeftAligned = 1
    CenterAligned = 2
    RightAligned = 3

# Used by
#	AttributeDefinitionInterface.Get
#	AttributeDefinitionInterface.Set
#	AttributeDefinitionInterface.Create
#	AttributeDefinitionInterface.GetFromDatabase
class AD_Owner(Enum):
    BlockConnector = 1
    BlockDevice = 2
    BlockPin = 3
    Bundle = 4
    Cable = 5
    CableCore = 6
    CableCoreEnd = 7
    CableEnd = 8
    CableType = 9
    CableTypeEnd = 10
    Component = 11
    ComponentPin = 12
    Connector = 13
    ConnectorPin = 14
    CoreType = 15
    CoreTypeEnd = 16
    DatabaseSymbol = 17
    Device = 18
    DevicePin = 19
    Dimension = 20
    FieldSymbol = 21
    FunctionalPort = 22
    FunctionalUnit = 23
    Graphic = 24
    Group = 25
    HoseTube = 26
    HoseTubeEnd = 27
    HoseTubeInside = 28 
    HoseTubeInsideEnd = 29
    HoseTubeInsideType = 30
    HoseTubeInsideTypeEnd = 31
    HoseTubeType = 32
    HoseTubeTypeEnd = 33
    Model = 34
    Module = 35
    Net = 36
    NetNode = 37
    NetSegment = 38
    Project = 39
    Sheet = 40
    SheetDatabase = 41
    Signal = 42
    SignalClass = 43
    SignalNode = 44
    Symbol = 45
    Text = 46
    VariantOptions = 47
    BusbarType = 48
    Busbar = 49


# Used by
#	AttributeDefinitionInterface.Get
#	AttributeDefinitionInterface.Set
#	AttributeDefinitionInterface.Create
#	AttributeDefinitionInterface.GetFromDatabase
class AD_Ratio(Enum):
    Normal = 1
    Narrow = 2
    Wide = 3

# Used by
#	AttributeDefinitionInterface.Get
#	AttributeDefinitionInterface.Set
#	AttributeDefinitionInterface.Create
#	AttributeDefinitionInterface.GetFromDatabase
class AD_Type(Enum):
    Integer = 1
    Real = 2
    LinearMeasure = 3
    String = 4
    Boolean = 5

# Used by
#	AttributeDefinitionInterface.Get
#	AttributeDefinitionInterface.Set
#	AttributeDefinitionInterface.Create
#	AttributeDefinitionInterface.GetFromDatabase
class AD_UniqueValue(Enum):
	NotUnique = 0
	Object = 1
	Project = 2
	Assignment = 3
	Location = 4
	AssignmentAndLocation = 5

# Used by
#   ComponentInterface.GetSubType
#   DbeComponentInterface.GetSubType
class ComponentSubType(Enum):
    NONE = 0
    Accessory = 1
    Fixture = 2
    ProtectionTube = 3
    ProtectionTape = 4
    Protector = 5
    Splice = 6
    JointConnector = 7

# Used by
#   ComponentInterface.GetComponentType
#   DbeComponentInterface.GetComponentType
class ComponentType(Enum):
    StandardDevice = 1
    Connector = 2
    ConnectorWithInserts = 3
    FeedThroughConnector = 4
    Terminal = 5
    Block = 6
    Assembly = 7
    CavityPartGroup = 8
    Subcircuit = 9
    Cable = 10
    WireGroup = 11
    Hose = 12
    Tube = 13
    Overbraid = 14
    Accessory = 15
    Fixture = 16
    ProtectionTube = 17
    ProtectionTape = 18
    Protector = 19
    Splice = 20
    CavityPlug = 21
    PinTerminal = 22
    WireSeal = 23
    Mount = 24
    CableDuct = 25
    CableDuctReference = 26
    CableDuctBackplanWire = 27
    CableDuctPunchingStrip = 28
    EndBracket = 29
    EndCover = 30
    SeparatingPlate = 31
    ComponentWithoutStructure = 32
    DynamicComponent = 33
    DynamicComponentDeviceStructureComponent = 34
    JointConnector = 35
    JigBoardClamp = 36
    Busbar = 37
    InsertGroup = 38
    MatingGroup = 39
    DynamicBlockComponent = 40
    DynamicConnectorComponent = 41

# Used by
#	Application.SetConfigFile
#	Application.GetConfigFile
#	DbeApplication.SetConfigFile
#	DbeApplication.GetConfigFile
class ConfigFileType(Enum):
	DXFImport = 1
	DXFExport = 2
	DGNImport = 3
	DGNExport = 4

# Used by
#   Slot.GetFixType()
class FixType(Enum):
    Point = 1
    Line = 2
    Area = 3
    Connect = 4

# Used by
#   GraphInterface.GetType
class GraphType(Enum):
    Line = 1
    Polygon = 2
    Rectangle = 3
    Circle = 4
    Arc = 5
    Group = 6
    Oval = 7
    Text = 8
    Block = 9
    OvalArc = 10
    DimensionLine = 11
    Image = 12

    Curve = 15
    Cloud = 16
    Blob = 17
    MIL_Line = 18

# Used by
#	JobInterface.GetItemType
class ItemType(Enum):
	Undefined = 0
	Project = 1
	Component = 2
	ComponentPin = 4
	SymbolType = 5
	Device = 10
	Gate = 11
	DevicePin = 12
	Block = 13
	BlockConnector = 14
	BlockConnectorPinGroup = 15
	BlockConnectorPin = 16
	Connector = 17
	ConnectorPinGroup = 18
	ConnectorPin = 19
	Cable = 20
	WireOrConductor = 22
	SignalOrSignalClass = 24
	Supply = 25
	AttributeDefinition = 26
	Attribute = 27
	Sheet = 28
	SheetReference = 29
	PlacedSymbolOrField = 30
	Text = 31
	ConnectLine = 32
	Node = 33
	Graphic = 34
	MenuItem35 = 35
	ProjectTreeOrMenuItem = 36
	MenuItem37 = 37
	Net = 38
	NetSegment = 39
	HierarchicalBlockOrModule = 46
	HierarchicalPort = 47
	Bundle = 50
	CableType = 51
	WireType = 52
	Slot = 59
	Contour = 60
	Position = 61
	MenuItem66 = 66
	MenuItem69 = 69
	MenuItem71 = 71
	FunctionalUnit = 72
	FunctionalPort = 73
	Group = 110
	MenuItem125 = 125
	Connection = 141
	ExternalDocument = 142
	MenuItem143 = 143
	Dimension = 151
	OptionOrVariant = 154
	PanelConnection = 156
	TestPoint = 163
	ClipboardOrStructureNode = 180
	MenuItem195 = 195
	MenuItem196 = 196
	StateItem = 200
	WireDifferenceItem = 201
	WireInformation = 202
	CavityPart = 208
	EmbeddedObject = 12292

# Used by
#   ApplictionInterface.GetModelList
class ModelType(Enum):
    Device = 1
    MountingRail = 2
    Busbar = 3
    CableDuct = 4
    PunchingStripCableDuct = 5
    CacleDuctInletOutlet = 6
    WireCombCableDuct = 7

# Used by
#   Pin.GetTypeId()
class PinType(Enum):
    DevicePin = 1
    ConnectorPin = 2
    BlockConnectorPin = 3
    ComponentPin = 4
    SymbolNode = 5
    ConnectorSymbolNode = 6
    NetNode = 7
    WireCountNode = 8
    TemplateSymbolNode = 9
    SheetReferenceNode = 10
    SignalCarryingNode = 11
    ConductorOrWire = 12
    Hose = 13
    Tube = 14
    ConductorOrWireDifferences = 15
    HoseDifferences = 16
    TubeDifferences = 17
    BusbarConductor = 18

# Used by
#   ApplictionInterface.GetProjectInformation
#   DbeApplictionInterface.GetProjectInformation
class ProjectType(Enum):
    Unsaved=0
    CableOrSchema = 1
    Logic = 2
    WireWorks = 3
    Demonstration = 4
    Student = 5

# Used by
#   SheetInterface.GetSchematicTypes
#   SheetInterface.SetSchematicTypes
class SchematicType(Enum):
    Electric = 0
    Hydraulic = 1
    Pneumatic = 2
    Process = 3
    Tubes = 4
    SingleLine = 5
    PanelSymbol = 6
 


# Used by
#   SymbolInterface.GetSymbolType
class SymbolType(Enum):
    Undefined = 0
    Arrow = 1
    # ASIC_or_FPGA = 2 # deprecated
    AttributeTextTemplate = 3
    Block = 4
    BlockConnector = 5
    Connector = 6
    ConnectorMaster = 7
    Table = 8
    ContactArrangementTemplate = 9
    GeneralTemplate = 10
    Bundle = 11
    ModulePort = 12
    NodeTemplate = 13
    Normal = 14
    # PadTemplate = 15 # deprecated
    PinTemplate = 16
    Shield = 17
    SignalCarrying = 18
    TerminalPlanJumper = 19
    TerminalPlanTable = 20
    TwistedPair = 21
    Accessory = 22
    Detail = 23
    MultiHolding = 24
    Fixture = 25
    HierarchicalDesignConnector = 26
    Figure = 27
    Reference = 28
    Model = 29
    Sheet = 30
    TerminalPlanSheet = 31
    PanelSheet = 32
    ConnectorPin = 33
    BackplaneEnd = 34
    Field = 35
    Dynamic = 36
    # HierarchicalPortOnSheet = 37 # deprecated
    MountingRail = 38
    Device = 39
    CableDuct = 40
    CableDuctReference = 41
    ConnectorFrontView = 42
    OpenEnd = 43
    JigBoardClamp = 44
    MILBlockConnector = 45
    MILConnector = 46
    MILFeedThroughConnector = 47

