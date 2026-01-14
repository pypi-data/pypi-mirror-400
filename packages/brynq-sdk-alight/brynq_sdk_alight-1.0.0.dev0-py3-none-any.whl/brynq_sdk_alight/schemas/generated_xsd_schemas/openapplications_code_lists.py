from enum import Enum

__NAMESPACE__ = "http://www.openapplications.org/oagis/9/codelists"


class ActionCodeEnumerationType(Enum):
    """
    The action values that OAGi defines for OAGIS.
    """

    ADD = "Add"
    CHANGE = "Change"
    DELETE = "Delete"
    REPLACE = "Replace"
    ACCEPTED = "Accepted"
    MODIFIED = "Modified"
    REJECTED = "Rejected"


class ChargeBearerCodeEnumerationType(Enum):
    """
    :cvar OUR: All transaction charges are to be borne by the debtor.
    :cvar BEN: All transaction charges are to be borne by the creditor.
    :cvar SHA: Transaction charges on the Sender's side are to be borne
        by the ordering customer. Transaction charges on the Receiver's
        side are to be borne by the beneficiary customer.
    """

    OUR = "OUR"
    BEN = "BEN"
    SHA = "SHA"


class ChequeDeliveryMethodCodeEnumerationType(Enum):
    """
    :cvar MLDB: Mail to Debitor
    :cvar MLCD: Mail to Creditor
    :cvar MLFA: Mail to Final agent
    :cvar CRDB: Courier to debtor
    :cvar CRCD: Courier to creditor
    :cvar CRFA: Courier to final agent
    :cvar PUDB: Pickup by debtor
    :cvar PUCD: Pickup by creditor
    :cvar PUFA: Pickup by final agent
    :cvar RGDB: Registered mail to debtor
    :cvar RGCD: Registered mail to creditor
    :cvar RGFA: Registered mail to final agent
    """

    MLDB = "MLDB"
    MLCD = "MLCD"
    MLFA = "MLFA"
    CRDB = "CRDB"
    CRCD = "CRCD"
    CRFA = "CRFA"
    PUDB = "PUDB"
    PUCD = "PUCD"
    PUFA = "PUFA"
    RGDB = "RGDB"
    RGCD = "RGCD"
    RGFA = "RGFA"


class ChequeInstructionCodeEnumerationType(Enum):
    CCHQ = "CCHQ"
    CCCH = "CCCH"
    BCHQ = "BCHQ"
    DFFT = "DFFT"
    ELDR = "ELDR"


class ContactLocationCodeEnumerationType(Enum):
    HOME = "Home"
    WORK = "Work"


class ControlAssertionEnumerationType(Enum):
    COMPLETENESS = "Completeness"
    EXISTENCE_OR_OCCURANCE = "Existence or Occurance"
    PRESENTATION_AND_DISCLOSURE = "Presentation and Disclosure"
    RIGHTS_AND_OBLIGATIONS = "Rights and Obligations"
    VALUATION_OR_MEASUREMENT = "Valuation or Measurement"


class ControlComponentEnumerationType(Enum):
    RISK_ASSESSMENT = "Risk Assessment"
    MONITORING = "Monitoring"
    CONTROL_ENVIRONMENT = "Control Environment"
    CONTROL_ACTIVITIES = "Control Activities"
    INFORMATION_AND_COMMUNICATION = "Information and Communication"


class CreditTransferCodeEnumerationType(Enum):
    """
    :cvar CASH: Cash management transfer.
    :cvar CORT: Payment made in settlement of a trade
    :cvar DIVI: Dividend.
    :cvar GOVT: Government payment.
    :cvar HEDG: Hedging
    :cvar INTC: Intra-company payment
    :cvar INTE: Interest
    :cvar LOAN: Loan. Transfer of loan to borrower.
    :cvar PENS: Pension payment
    :cvar SALA: Salary payment
    :cvar SECU: Securities.
    :cvar SSBE: Social security benefit. Payment made by government to
        support individuals.
    :cvar SUPP: Supplier payment
    :cvar TAXS: Tax payment
    :cvar TRAD: Trade.
    :cvar TREA: Treasury payment
    :cvar VATX: Value added Tax payment
    """

    CASH = "CASH"
    CORT = "CORT"
    DIVI = "DIVI"
    GOVT = "GOVT"
    HEDG = "HEDG"
    INTC = "INTC"
    INTE = "INTE"
    LOAN = "LOAN"
    PENS = "PENS"
    SALA = "SALA"
    SECU = "SECU"
    SSBE = "SSBE"
    SUPP = "SUPP"
    TAXS = "TAXS"
    TRAD = "TRAD"
    TREA = "TREA"
    VATX = "VATX"


class DayOfWeekCodeEnumerationType(Enum):
    SUNDAY = "Sunday"
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"


class DebitCreditCodeEnumerationType(Enum):
    DEBIT = "Debit"
    CREDIT = "Credit"


class EmailFormatCodeEnumerationType(Enum):
    HTML = "HTML"
    RICH_TEXT = "Rich Text"
    PLAIN_TEXT = "Plain Text"


class EngineeringActivityCodeEnumerationType(Enum):
    """
    :cvar AMENDMENT: An activity to add information to product data
    :cvar ANALYSIS: An activity to determine the behavior of an element
        under certain physical circumstances
    :cvar CANCELLATION: An activity to delete an element from the bill
        of material or to cancel he whole bill of material
    :cvar DELIVERY_CHANGE: An actity to change the delivery schedule of
        an element
    :cvar DESIGN_CHANGE: An activity to change the design of an item or
        an assembly; this might include changes to the geometry or to
        the properties of the object
    :cvar DESIGN: An activity concerning the development of a design of
        an item
    :cvar MOCK_UP_CREATION: An activity to create an experimental model
        or replica of an item
    :cvar PROTOYPE_BUILDING: An activity to manufacture a preliminary
        version of an item
    :cvar RECTIFICATION: An activity to correct the data, documentation
        or structure associated wih an item
    :cvar RESTRUCTURING: An activity to create an new structure or
        position within a bill of material without changin the data
        associated with the items in the bill of material
    :cvar SPARE_PART_CREATION: An activity to design a spare part or to
        classify an item as a spare part
    :cvar STOP_NOTICE: An activity to stop the manufacturing process of
        an item
    :cvar TESTING: An activity to test an item
    """

    AMENDMENT = "amendment"
    ANALYSIS = "analysis"
    CANCELLATION = "cancellation"
    DELIVERY_CHANGE = "deliveryChange"
    DESIGN_CHANGE = "designChange"
    DESIGN = "design"
    MOCK_UP_CREATION = "mockUpCreation"
    PROTOYPE_BUILDING = "protoypeBuilding"
    RECTIFICATION = "rectification"
    RESTRUCTURING = "restructuring"
    SPARE_PART_CREATION = "sparePartCreation"
    STOP_NOTICE = "stopNotice"
    TESTING = "testing"


class EngineeringWorkOrderCodeEnumerationType(Enum):
    """
    Identifies the type of Engineering Work Order.

    :cvar DESIGN_DEVIATION_PERMIT: An authorization for a deviation from
        the approved design data
    :cvar DESIGN_RELEASE: An auhorization for the design of a product or
        of an item or o create a bill of material
    :cvar MANAGEMENT_RESOLUTION: An authorization by a committee, such
        as the board of directos, to design or change an item
    :cvar MANUFACTURING_RELEASE: An authorization for the manufacturing
        process of a product or of an item
    :cvar PRODUCTION_DEVIATION_PERMIT: An authorization for a deviation
        from the approved manufacturing process
    """

    DESIGN_DEVIATION_PERMIT = "designDeviationPermit"
    DESIGN_RELEASE = "designRelease"
    MANAGEMENT_RESOLUTION = "managementResolution"
    MANUFACTURING_RELEASE = "manufacturingRelease"
    PRODUCTION_DEVIATION_PERMIT = "productionDeviationPermit"


class EngineeringWorkRequestCodeEnumerationType(Enum):
    """
    Identifies the type of Engineering Work Request.

    :cvar CHANGE_OF_STANDARD: A request to translate a change to a
        standard into action
    :cvar COST_REDUCTION: A request aimed at reducing the engineering
        and manufacturing costs of an item
    :cvar CUSTOMER_REJECTION: A request resulting from a rejection by a
        customer
    :cvar CUSTOMER_REQUEST: A request for an activity that is necessary
        to solve the request of a customer
    :cvar DURABILITY_IMPROVEMENT: A request aimed at extending the life
        time of an item
    :cvar GOVERNMENT_REGULATION: A request resulting from legal
        requirements
    :cvar PROCUREMENT_ALIGNMENT:
    :cvar PRODUCTION_ALIGNMENT:
    :cvar PRODUCTION_RELIEF:
    :cvar PRODUCTION_REQUIREMENT:
    :cvar QUALITY_IMPROVEMENT:
    :cvar SECURIY_REASON:
    :cvar STANDARDIZATION:
    :cvar SUPPLIER_REQUEST:
    :cvar TECHNICAL_IMPROVEMENT:
    :cvar TOOL_IMPROVEMENT:
    """

    CHANGE_OF_STANDARD = "ChangeOfStandard"
    COST_REDUCTION = "CostReduction"
    CUSTOMER_REJECTION = "CustomerRejection"
    CUSTOMER_REQUEST = "CustomerRequest"
    DURABILITY_IMPROVEMENT = "DurabilityImprovement"
    GOVERNMENT_REGULATION = "GovernmentRegulation"
    PROCUREMENT_ALIGNMENT = "ProcurementAlignment"
    PRODUCTION_ALIGNMENT = "ProductionAlignment"
    PRODUCTION_RELIEF = "ProductionRelief"
    PRODUCTION_REQUIREMENT = "ProductionRequirement"
    QUALITY_IMPROVEMENT = "QualityImprovement"
    SECURIY_REASON = "SecuriyReason"
    STANDARDIZATION = "Standardization"
    SUPPLIER_REQUEST = "SupplierRequest"
    TECHNICAL_IMPROVEMENT = "TechnicalImprovement"
    TOOL_IMPROVEMENT = "ToolImprovement"


class FinalAgentInstructionCodeEnumerationType(Enum):
    """
    :cvar CHQB: Pay creditor only by cheque. The creditor's account
        number must not be specified.
    :cvar HOLD: Hold cash for creditor. Creditor will call; pay upon
        identification.
    :cvar PHOB: Please advise/contact beneficiary/claimant by phone.
    :cvar TELB: Please advise/contact beneficiary/claimant by the most
        efficient means of telecommunication.
    """

    CHQB = "CHQB"
    HOLD = "HOLD"
    PHOB = "PHOB"
    TELB = "TELB"


class GenderCodeEnumerationType(Enum):
    MALE = "Male"
    FEMALE = "Female"
    UNKNOWN = "Unknown"


class LicenseTypeCodeEnumerationType(Enum):
    IMPORT = "Import"
    EXPORT = "Export"


class MaritalStatusCodeEnumerationType(Enum):
    DIVORCED = "Divorced"
    MARRIED = "Married"
    NEVER_MARRIED = "NeverMarried"
    SEPARATED = "Separated"
    SIGNIFICANT_OTHER = "SignificantOther"
    WIDOWED = "Widowed"
    UNKNOWN = "Unknown"


class MatchCodeEnumerationType(Enum):
    """Standard List of Invoice Matching Types.

    2 stands for two way matching (Invoice, PO). 3 stands for three way
    matching (Invoice, PO, Receipt). 4 stands for four way matching
    (Invoice, PO, Receipt, Invoice)
    """

    VALUE_2 = "2"
    VALUE_3 = "3"
    VALUE_4 = "4"


class MatchDocumentEnumerationType(Enum):
    INVOICE = "Invoice"
    PURCHASE_ORDER = "Purchase Order"
    RECEIPT = "Receipt"
    INSPECTION = "Inspection"


class PartyCategoryCodeEnumerationType(Enum):
    """
    This list of Party Categories.
    """

    ORGANIZATION = "Organization"
    INDIVIDUAL = "Individual"


class PaymentBasisCodeEnumerationType(Enum):
    """
    This list is the agreed to sub set of Payment Term Basis Codes from X12 Element
    333.
    """

    INVOICE_DATE = "InvoiceDate"
    SHIPPING_DATE = "ShippingDate"
    DELIVERY_DATE = "DeliveryDate"
    PURCHASE_ORDER_DATE = "PurchaseOrderDate"
    RECEIPT_OF_GOODS_DATE = "ReceiptOfGoodsDate"
    ACCEPTANCE_OF_GOODS_DATE = "AcceptanceOfGoodsDate"
    ACCEPTANCE_OF_ORDER_DATE = "AcceptanceOfOrderDate"


class PaymentMethodCodeEnumerationType(Enum):
    CASH = "Cash"
    CHEQUE = "Cheque"
    CREDIT_CARD = "CreditCard"
    DEBIT_CARD = "DebitCard"
    ELECTRONIC_FUNDS_TRANSFER = "ElectronicFundsTransfer"
    PROCUREMENT_CARD = "ProcurementCard"
    BANK_DRAFT = "BankDraft"
    PURCHASE_ORDER = "PurchaseOrder"
    CREDIT_TRANSFER = "CreditTransfer"


class PaymentPurposeCodeEnumerationType(Enum):
    ADVA = "ADVA"
    AGRT = "AGRT"
    ALMY = "ALMY"
    BECH = "BECH"
    BENE = "BENE"
    BONU = "BONU"
    CASH = "CASH"
    CBFF = "CBFF"
    CHAR = "CHAR"
    CMDT = "CMDT"
    COLL = "COLL"
    COMC = "COMC"
    COMM = "COMM"
    CONS = "CONS"
    COST = "COST"
    CPYR = "CPYR"
    DBTC = "DBTC"
    DIVI = "DIVI"
    FREX = "FREX"
    GDDS = "GDDS"
    GOVT = "GOVT"
    HEDG = "HEDG"
    IHRP = "IHRP"
    INSU = "INSU"
    INTC = "INTC"
    INTE = "INTE"
    LICF = "LICF"
    LOAN = "LOAN"
    LOAR = "LOAR"
    NETT = "NETT"
    PAYR = "PAYR"
    PENS = "PENS"
    REFU = "REFU"
    RENT = "RENT"
    ROYA = "ROYA"
    SALA = "SALA"
    SCVE = "SCVE"
    SECU = "SECU"
    SSBE = "SSBE"
    SUBS = "SUBS"
    TAXS = "TAXS"
    TREA = "TREA"
    VATX = "VATX"
    VENP = "VENP"


class PaymentSchemeCodeEnumerationType(Enum):
    """
    :cvar ACH: Payment has to be executed through an Automated Clearing
        House
    :cvar RTGS: Payment has to be executed through Real time gross
        settlement system.
    :cvar FEDNET: Payment has to be executed through FedNet
    :cvar CHIPS: Payment has to be executed through CHIPS.
    """

    ACH = "ACH"
    RTGS = "RTGS"
    FEDNET = "Fednet"
    CHIPS = "CHIPS"


class PaymentTermCodeEnumerationType(Enum):
    NET20 = "Net20"
    NET30 = "Net30"
    NET45 = "Net45"
    NET60 = "Net60"
    VALUE_10_PERCENT30 = "10Percent30"


class ProcessCategoryEnumerationType(Enum):
    """Processes may be categorized as Routine, Non-Routine or Estimating.

    An example of a Routine Process is recording costs of goods sold. An
    example of a Non-Routine Process is recording Inventory Adjustments.
    An example of an Estimating Process is determining Inventory
    Obsolsence. Estimating Processes give wide lattitude to move the
    profit figure and attract a high degree of scrutiny. Non Routine
    Processes tend to have fewer controls in place and are exposed to
    more risks.
    """

    ROUTINE = "Routine"
    NON_ROUTINE = "Non-Routine"
    ESTIMATING = "Estimating"


class RecurrencePatternCodeEnumerationType(Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    YEARLY = "Yearly"


class RemitLocationMethodCodeEnumerationType(Enum):
    """
    :cvar FAX: Remittance advice information needs to be faxed.
    :cvar EDI: Remittance advice information needs to be sent through
        Electronic Data Interchange.
    :cvar URI: Remittance advice information needs to be sent to a
        Uniform Resource Identifier (URI). URI is a compact string of
        characters that uniquely identify an abstract or physical
        resource. URI's are the super-set of identifiers, such as URLs,
        email addresses, ftp sites, etc, and as such, provide the syntax
        for all of the identification schemes.
    :cvar EML:
    :cvar PST:
    """

    FAX = "FAX"
    EDI = "EDI"
    URI = "URI"
    EML = "EML"
    PST = "PST"


class ResponseActionCodeEnumerationType(Enum):
    """
    The action values that OAGi defines for OAGIS.
    """

    ACCEPTED = "Accepted"
    MODIFIED = "Modified"
    REJECTED = "Rejected"


class ResponseCodeEnumerationType(Enum):
    """
    The acknowledge values that OAGi defines for OAGIS.
    """

    ALWAYS = "Always"
    ON_ERROR = "OnError"
    NEVER = "Never"


class RiskTypeEnumerationType(Enum):
    COMPLIANCE_WITH_APPLICABLE_LAWS_AND_REGULATIONS = (
        "Compliance with applicable laws and regulations"
    )
    EFFECTIVENESS_AND_EFFICIENCY_OF_OPERATIONS = (
        "Effectiveness and efficiency of operations"
    )
    RELIABILITY_OF_FINANCIAL_STATEMENTS = "Reliability of Financial Statements"


class SalesActivityCodeEnumerationType(Enum):
    LITERATURE_REQUEST = "LiteratureRequest"
    NEW_LEAD = "NewLead"
    DEAD_CONTENT = "DeadContent"
    TRAFFIC_REPORT = "TrafficReport"
    SOLD = "Sold"
    EMAIL = "EMail"
    LETTER = "Letter"
    FAX = "Fax"


class SalesTaskCodeEnumerationType(Enum):
    MEETING = "Meeting"
    CONFERENCE_CALL = "ConferenceCall"
    FOLLOW_UP = "FollowUp"
    EMAIL = "EMail"


class SystemEnvironmentCodeEnumerationType(Enum):
    PRODUCTION = "Production"
    TEST = "Test"


class TransferCodeEnumerationType(Enum):
    COMPLETE = "Complete"
    RETURN = "Return"
