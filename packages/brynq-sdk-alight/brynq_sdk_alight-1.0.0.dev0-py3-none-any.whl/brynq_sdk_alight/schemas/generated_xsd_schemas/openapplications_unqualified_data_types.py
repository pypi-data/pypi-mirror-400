from decimal import Decimal
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field

from .openapplications_code_list_currency_code_iso_7_04 import (
    CurrencyCodeContentType,
)

__NAMESPACE__ = (
    "http://www.openapplications.org/oagis/9/unqualifieddatatypes/1.1"
)


class BinaryObjectType(BaseModel):
    """<ns1:UniqueID
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000002</ns1:UniqueID>
    <ns1:CategoryCode
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT</ns1:CategoryCode>
    <ns1:DictionaryEntryName
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Binary Object.

    Type</ns1:DictionaryEntryName>
    <ns1:VersionID xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">1.0</ns1:VersionID>
    <ns1:Definition xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">A set of finite-length sequences of binary octets.</ns1:Definition>
    <ns1:RepresentationTermName xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Binary Object</ns1:RepresentationTermName>
    <ns1:PrimitiveType xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">binary</ns1:PrimitiveType>

    :ivar value:
    :ivar format: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000002-SC2</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Binary
        Object. Format. Text</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The format
        of the binary content.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Binary
        Object</ns1:ObjectClass> <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Format</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Text</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar mime_code: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000002-SC3</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Binary
        Object. Mime. Code</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The mime
        type of the binary object.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Binary
        Object</ns1:ObjectClass> <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Mime</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar encoding_code: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000002-SC4</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Binary
        Object. Encoding. Code</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Specifies
        the decoding algorithm of the binary object.</ns1:Definition>
        <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Binary
        Object</ns1:ObjectClass> <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Encoding</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar character_set_code: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000002-SC5</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Binary
        Object. Character Set. Code</ns1:DictionaryEntryName>
        <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The
        character set of the binary object if the mime type is
        text.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Binary
        Object</ns1:ObjectClass> <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Character
        Set</ns1:PropertyTermName> <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar uri: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000002-SC6</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Binary
        Object. Uniform Resource. Identifier</ns1:DictionaryEntryName>
        <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The Uniform
        Resource Identifier that identifies where the binary object is
        located.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Binary
        Object</ns1:ObjectClass> <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Uniform
        Resource Identifier</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identifier</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar filename: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000002-SC7</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Binary
        Object. Filename.Text</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The filename
        of the binary object.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Binary
        Object</ns1:ObjectClass> <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Filename</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Text</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    """

    model_config = ConfigDict(defer_build=True)
    value: bytes = field(
        metadata={
            "required": True,
            "format": "base64",
        }
    )
    format: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    mime_code: str = field(
        metadata={
            "name": "mimeCode",
            "type": "Attribute",
            "required": True,
        }
    )
    encoding_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "encodingCode",
            "type": "Attribute",
        },
    )
    character_set_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "characterSetCode",
            "type": "Attribute",
        },
    )
    uri: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    filename: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class CodeType(BaseModel):
    """<ns1:UniqueID
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000007</ns1:UniqueID>
    <ns1:CategoryCode
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT</ns1:CategoryCode>
    <ns1:DictionaryEntryName
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code.

    Type</ns1:DictionaryEntryName>
    <ns1:VersionID xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">1.0</ns1:VersionID>
    <ns1:Definition xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">A character string (letters, figures, or symbols) that for brevity and/or languange independence may be used to
    represent or replace a definitive value or text of an attribute together with relevant supplementary
    information.</ns1:Definition>
    <ns1:RepresentationTermName xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code</ns1:RepresentationTermName>
    <ns1:PrimitiveType xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    <ns1:UsageRule xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Other supplementary components in the CCT are captured as part of the token and name for the schema module containing
    the code list and thus, are not declared as attributes. </ns1:UsageRule>

    :ivar value:
    :ivar list_id: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UNDT000007-SC2</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code List.
        Identifier</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The
        identification of a list of codes.</ns1:Definition>
        <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code
        List</ns1:ObjectClass> <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identification</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identifier</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar list_agency_id: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UNDT000007-SC3</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code List.
        Agency. Identifier</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">An agency
        that maintains one or more lists of codes.</ns1:Definition>
        <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code
        List</ns1:ObjectClass> <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Agency</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identifier</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
        <ns1:UsageRule
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Defaults to
        the UN/EDIFACT data element 3055 code list.</ns1:UsageRule>
    :ivar list_agency_name: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UNDT000007-SC4</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code List.
        Agency Name. Text</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The name of
        the agency that maintains the list of codes.</ns1:Definition>
        <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code
        List</ns1:ObjectClass> <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Agency
        Name</ns1:PropertyTermName> <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Text</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar list_name: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UNDT000007-SC5</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code List.
        Name. Text</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The name of
        a list of codes.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code
        List</ns1:ObjectClass> <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Name</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Text</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar list_version_id: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UNDT000007-SC6</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code List.
        Identifier</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The
        identification of a list of codes.</ns1:Definition>
        <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code
        List</ns1:ObjectClass> <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identification</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identifier</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar name: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000007-SC7</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code. Name.
        Text</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The textual
        equivalent of the code content component.</ns1:Definition>
        <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code</ns1:ObjectClass>
        <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Name</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Text</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar language_id: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000007-SC8</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Language.
        Identifier</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The
        identifier of the language used in the code
        name.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Language</ns1:ObjectClass>
        <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identification</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identifier</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar list_uri: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000007-SC9</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code List.
        Uniform Resource. Identifier</ns1:DictionaryEntryName>
        <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The Uniform
        Resource Identifier that identifies where the code list is
        located.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code
        List</ns1:ObjectClass> <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Uniform
        Resource Identifier</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identifier</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar list_scheme_uri: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000007-SC10</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code List
        Scheme. Uniform Resource. Identifier</ns1:DictionaryEntryName>
        <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The Uniform
        Resource Identifier that identifies where the code list scheme
        is located.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code List
        Scheme</ns1:ObjectClass> <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Uniform
        Resource Identifier</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identifier</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    """

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    list_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "listID",
            "type": "Attribute",
        },
    )
    list_agency_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "listAgencyID",
            "type": "Attribute",
        },
    )
    list_agency_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "listAgencyName",
            "type": "Attribute",
        },
    )
    list_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "listName",
            "type": "Attribute",
        },
    )
    list_version_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "listVersionID",
            "type": "Attribute",
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    language_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "languageID",
            "type": "Attribute",
        },
    )
    list_uri: Optional[str] = field(
        default=None,
        metadata={
            "name": "listURI",
            "type": "Attribute",
        },
    )
    list_scheme_uri: Optional[str] = field(
        default=None,
        metadata={
            "name": "listSchemeURI",
            "type": "Attribute",
        },
    )


class GraphicType(BaseModel):
    """<ns1:UniqueID
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000003</ns1:UniqueID>
    <ns1:CategoryCode
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT</ns1:CategoryCode>
    <ns1:DictionaryEntryName
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Graphic.

    Type</ns1:DictionaryEntryName>
    <ns1:VersionID xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">1.0</ns1:VersionID>
    <ns1:Definition xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">A diagram, graph, mathematical curves, or similar representation.</ns1:Definition>
    <ns1:RepresentationTermName xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Graphic</ns1:RepresentationTermName>
    <ns1:PrimitiveType xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">binary</ns1:PrimitiveType>

    :ivar value:
    :ivar format: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000003-SC2</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Graphic.
        Format. Text</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The format
        of the graphic content.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Graphic</ns1:ObjectClass>
        <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Format</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Text</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar mime_code: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000003-SC3</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Graphic.
        Mime. Code</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The mime
        type of the graphic object.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Graphic</ns1:ObjectClass>
        <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Mime</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar encoding_code: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000003-SC4</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Graphic.
        Encoding. Code</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Specifies
        the decoding algorithm of the graphic object.</ns1:Definition>
        <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Graphic</ns1:ObjectClass>
        <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Encoding</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar uri: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000003-SC6</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Graphic.
        Uniform Resource. Identifier</ns1:DictionaryEntryName>
        <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The Uniform
        Resource Identifier that identifies where the graphic object is
        located.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Graphic</ns1:ObjectClass>
        <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Uniform
        Resource Identifier</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identifier</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar filename: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000003-SC7</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Graphic.
        Filename.Text</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The filename
        of the graphic object.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Graphic</ns1:ObjectClass>
        <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Filename</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Text</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    """

    model_config = ConfigDict(defer_build=True)
    value: bytes = field(
        metadata={
            "required": True,
            "format": "base64",
        }
    )
    format: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    mime_code: str = field(
        metadata={
            "name": "mimeCode",
            "type": "Attribute",
            "required": True,
        }
    )
    encoding_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "encodingCode",
            "type": "Attribute",
        },
    )
    uri: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    filename: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class IdentifierType(BaseModel):
    """<ns1:UniqueID xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT0000011
    </ns1:UniqueID> <ns1:CategoryCode
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT</ns1:CategoryCode>
    <ns1:DictionaryEntryName
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identifier.

    Type</ns1:DictionaryEntryName>
    <ns1:VersionID xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">1.0</ns1:VersionID>
    <ns1:Definition xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">A character string to identify and distinguish uniquely, one instance of an object in an identification scheme from
    all other objects in the same scheme together with relevant supplementary information.</ns1:Definition>
    <ns1:RepresentationTermName xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identifier</ns1:RepresentationTermName>
    <ns1:PrimitiveType xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    <ns1:UsageRule xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Other supplementary components in the CCT are captured as part of the token and name for the schema module containing
    the identifer list and thus, are not declared as attributes. </ns1:UsageRule>

    :ivar value:
    :ivar scheme_id: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UNDT000011-SC2</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identification
        Scheme. Identifier</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The
        identification of the identification scheme.</ns1:Definition>
        <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identification
        Scheme</ns1:ObjectClass> <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identification</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identifier</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar scheme_name: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UNDT000011-SC3</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identification
        Scheme. Name. Text</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The name of
        the identification scheme.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identification
        Scheme</ns1:ObjectClass> <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Name</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Text</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar scheme_agency_id: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UNDT000011-SC4</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identification
        Scheme Agency. Identifier</ns1:DictionaryEntryName>
        <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The
        identification of the agency that maintains the identification
        scheme.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identification
        Scheme Agency</ns1:ObjectClass> <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identification</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identifier</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
        <ns1:UsageRule
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Defaults to
        the UN/EDIFACT data element 3055 code list.</ns1:UsageRule>
    :ivar scheme_agency_name: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UNDT000011-SC5</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identification
        Scheme Agency. Name. Text</ns1:DictionaryEntryName>
        <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The name of
        the agency that maintains the identification
        scheme.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identification
        Scheme Agency</ns1:ObjectClass> <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Agency
        Name</ns1:PropertyTermName> <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Text</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar scheme_version_id: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UNDT000011-SC6</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identification
        Scheme. Version. Identifier</ns1:DictionaryEntryName>
        <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The version
        of the identification scheme.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identification
        Scheme</ns1:ObjectClass> <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Version</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identifier</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar scheme_data_uri: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT0000011-SC7</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identification
        Scheme Data. Uniform Resource.
        Identifier</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The Uniform
        Resource Identifier that identifies where the identification
        scheme data is located.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identification
        Scheme Data</ns1:ObjectClass> <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Uniform
        Resource Identifier</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identifier</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar scheme_uri: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT0000011-SC8</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identification
        Scheme. Uniform Resource. Identifier</ns1:DictionaryEntryName>
        <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The Uniform
        Resource Identifier that identifies where the identification
        scheme is located.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identification
        Scheme</ns1:ObjectClass> <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Uniform
        Resource Identifier</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identifier</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    """

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    scheme_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "schemeID",
            "type": "Attribute",
        },
    )
    scheme_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "schemeName",
            "type": "Attribute",
        },
    )
    scheme_agency_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "schemeAgencyID",
            "type": "Attribute",
        },
    )
    scheme_agency_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "schemeAgencyName",
            "type": "Attribute",
        },
    )
    scheme_version_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "schemeVersionID",
            "type": "Attribute",
        },
    )
    scheme_data_uri: Optional[str] = field(
        default=None,
        metadata={
            "name": "schemeDataURI",
            "type": "Attribute",
        },
    )
    scheme_uri: Optional[str] = field(
        default=None,
        metadata={
            "name": "schemeURI",
            "type": "Attribute",
        },
    )


class MeasureType(BaseModel):
    """<ns1:UniqueID xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT0000013
    </ns1:UniqueID> <ns1:CategoryCode
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT</ns1:CategoryCode>
    <ns1:DictionaryEntryName
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Measure.

    Type</ns1:DictionaryEntryName>
    <ns1:VersionID xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">1.0</ns1:VersionID>
    <ns1:Definition xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">A numeric value determined by measuring an object along with the specified unit of measure.</ns1:Definition>
    <ns1:RepresentationTermName xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Measure</ns1:RepresentationTermName>
    <ns1:PropertyTermName xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Type</ns1:PropertyTermName>
    <ns1:PrimitiveType xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">decimal</ns1:PrimitiveType>

    :ivar value:
    :ivar unit_code: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT0000013-SC2</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Measure
        Unit. Code</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The type of
        unit of measure.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Measure
        Unit</ns1:ObjectClass> <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
        <ns1:UsageRule
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Reference
        UN/ECE Rec 20 and X12 355.</ns1:UsageRule>
    """

    model_config = ConfigDict(defer_build=True)
    value: Decimal = field(
        metadata={
            "required": True,
        }
    )
    unit_code: str = field(
        metadata={
            "name": "unitCode",
            "type": "Attribute",
            "required": True,
        }
    )


class NameType(BaseModel):
    """<ns1:UniqueID xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT0000020
    </ns1:UniqueID> <ns1:CategoryCode
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT</ns1:CategoryCode>
    <ns1:DictionaryEntryName
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Name.

    Type</ns1:DictionaryEntryName>
    <ns1:VersionID xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">1.0</ns1:VersionID>
    <ns1:Definition xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">A character string that consititues the distinctive designation of a person, place, thing or
    concept.</ns1:Definition>
    <ns1:RepresentationTermName xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Name</ns1:RepresentationTermName>
    <ns1:PrimitiveType xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>

    :ivar value:
    :ivar language_id: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT0000020-SC2</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Language.
        Identifier</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The
        identifier of the language used in the content
        component.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Language</ns1:ObjectClass>
        <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identification</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identifier</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    """

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    language_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "languageID",
            "type": "Attribute",
        },
    )


class PictureType(BaseModel):
    """<ns1:UniqueID
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000004</ns1:UniqueID>
    <ns1:CategoryCode
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT</ns1:CategoryCode>
    <ns1:DictionaryEntryName
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Picture.

    Type</ns1:DictionaryEntryName>
    <ns1:VersionID xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">1.0</ns1:VersionID>
    <ns1:Definition xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">A diagram, graph, mathematical curves, or similar representation.</ns1:Definition>
    <ns1:RepresentationTermName xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Picture</ns1:RepresentationTermName>
    <ns1:PrimitiveType xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">binary</ns1:PrimitiveType>

    :ivar value:
    :ivar format: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000004-SC2</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Picture.
        Format. Text</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The format
        of the picture content.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Picture</ns1:ObjectClass>
        <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Format</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Text</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar mime_code: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000004-SC3</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Picture.
        Mime. Code</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The mime
        type of the picture object.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Picture</ns1:ObjectClass>
        <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Mime</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar encoding_code: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000004-SC4</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Picture.
        Encoding. Code</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Specifies
        the decoding algorithm of the picture object.</ns1:Definition>
        <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Picture</ns1:ObjectClass>
        <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Encoding</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar uri: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000004-SC6</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Picture.
        Uniform Resource. Identifier</ns1:DictionaryEntryName>
        <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The Uniform
        Resource Identifier that identifies where the picture object is
        located.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Picture</ns1:ObjectClass>
        <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Uniform
        Resource Identifier</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identifier</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar filename: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000004-SC7</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Picture.
        Filename.Text</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The filename
        of the picture object.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Picture</ns1:ObjectClass>
        <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Filename</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Text</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    """

    model_config = ConfigDict(defer_build=True)
    value: bytes = field(
        metadata={
            "required": True,
            "format": "base64",
        }
    )
    format: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    mime_code: str = field(
        metadata={
            "name": "mimeCode",
            "type": "Attribute",
            "required": True,
        }
    )
    encoding_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "encodingCode",
            "type": "Attribute",
        },
    )
    uri: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    filename: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class QuantityType(BaseModel):
    """<ns1:UniqueID xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT0000018
    </ns1:UniqueID> <ns1:CategoryCode
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT</ns1:CategoryCode>
    <ns1:DictionaryEntryName
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Quantity.

    Type</ns1:DictionaryEntryName>
    <ns1:VersionID xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">1.0</ns1:VersionID>
    <ns1:Definition xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">A counted number of non-monetary units possibly including fractions.</ns1:Definition>
    <ns1:RepresentationTermName xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Quantity</ns1:RepresentationTermName>
    <ns1:PrimitiveType xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">decimal</ns1:PrimitiveType>

    :ivar value:
    :ivar unit_code: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT0000018-SC2</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Quantity.
        Unit. Code</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The unit of
        the quantity</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Quantity</ns1:ObjectClass>
        <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Unit
        Code</ns1:PropertyTermName> <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    """

    model_config = ConfigDict(defer_build=True)
    value: Decimal = field(
        metadata={
            "required": True,
        }
    )
    unit_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "unitCode",
            "type": "Attribute",
        },
    )


class SoundType(BaseModel):
    """<ns1:UniqueID
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000005</ns1:UniqueID>
    <ns1:CategoryCode
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT</ns1:CategoryCode>
    <ns1:DictionaryEntryName
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Sound.

    Type</ns1:DictionaryEntryName>
    <ns1:VersionID xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">1.0</ns1:VersionID>
    <ns1:Definition xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">A diagram, graph, mathematical curves, or similar representation.</ns1:Definition>
    <ns1:RepresentationTermName xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Sound</ns1:RepresentationTermName>
    <ns1:PrimitiveType xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">binary</ns1:PrimitiveType>

    :ivar value:
    :ivar format: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000005-SC2</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Sound.
        Format. Text</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The format
        of the sound content.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Sound</ns1:ObjectClass>
        <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Format</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Text</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar mime_code: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000005-SC3</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Sound. Mime.
        Code</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The mime
        type of the sound object.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Sound</ns1:ObjectClass>
        <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Mime</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar encoding_code: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000005-SC4</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Sound.
        Encoding. Code</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Specifies
        the decoding algorithm of the sound object.</ns1:Definition>
        <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Sound</ns1:ObjectClass>
        <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Encoding</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar uri: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000005-SC6</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Sound.
        Uniform Resource. Identifier</ns1:DictionaryEntryName>
        <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The Uniform
        Resource Identifier that identifies where the sound object is
        located.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Sound</ns1:ObjectClass>
        <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Uniform
        Resource Identifier</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identifier</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar filename: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000005-SC7</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Sound.
        Filename.Text</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The filename
        of the sound object.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Sound</ns1:ObjectClass>
        <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Filename</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Text</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    """

    model_config = ConfigDict(defer_build=True)
    value: bytes = field(
        metadata={
            "required": True,
            "format": "base64",
        }
    )
    format: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    mime_code: str = field(
        metadata={
            "name": "mimeCode",
            "type": "Attribute",
            "required": True,
        }
    )
    encoding_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "encodingCode",
            "type": "Attribute",
        },
    )
    uri: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    filename: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class TextType(BaseModel):
    """<ns1:UniqueID xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT0000019
    </ns1:UniqueID> <ns1:CategoryCode
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT</ns1:CategoryCode>
    <ns1:DictionaryEntryName
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Text.

    Type</ns1:DictionaryEntryName>
    <ns1:VersionID xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">1.0</ns1:VersionID>
    <ns1:Definition xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">A character string (i.e. a finite set of characters) generally in the form of words of a language.</ns1:Definition>
    <ns1:RepresentationTermName xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Text</ns1:RepresentationTermName>
    <ns1:PrimitiveType xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>

    :ivar value:
    :ivar language_id: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT0000019-SC2</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Language.
        Identifier</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The
        identifier of the language used in the content
        component.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Language</ns1:ObjectClass>
        <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identification</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identifier</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    """

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    language_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "languageID",
            "type": "Attribute",
        },
    )


class VideoType(BaseModel):
    """<ns1:UniqueID
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000006</ns1:UniqueID>
    <ns1:CategoryCode
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT</ns1:CategoryCode>
    <ns1:DictionaryEntryName
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Video.

    Type</ns1:DictionaryEntryName>
    <ns1:VersionID xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">1.0</ns1:VersionID>
    <ns1:Definition xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">A diagram, graph, mathematical curves, or similar representation.</ns1:Definition>
    <ns1:RepresentationTermName xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Graphic</ns1:RepresentationTermName>
    <ns1:PrimitiveType xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">binary</ns1:PrimitiveType>

    :ivar value:
    :ivar format: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000006-SC2</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Video.
        Format. Text</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The format
        of the video content.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Video</ns1:ObjectClass>
        <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Format</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Text</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar mime_code: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000006-SC3</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Video. Mime.
        Code</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The mime
        type of the video object.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Video</ns1:ObjectClass>
        <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Mime</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar encoding_code: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000006-SC4</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Video.
        Encoding. Code</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Specifies
        the decoding algorithm of the video object.</ns1:Definition>
        <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Video</ns1:ObjectClass>
        <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Encoding</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Code</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar uri: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000006-SC6</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Video.
        Uniform Resource. Identifier</ns1:DictionaryEntryName>
        <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The Uniform
        Resource Identifier that identifies where the video object is
        located.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Video</ns1:ObjectClass>
        <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Uniform
        Resource Identifier</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identifier</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    :ivar filename: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000006-SC7</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Video.
        Filename.Text</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The filename
        of the video object.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Video</ns1:ObjectClass>
        <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Filename</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Text</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    """

    model_config = ConfigDict(defer_build=True)
    value: bytes = field(
        metadata={
            "required": True,
            "format": "base64",
        }
    )
    format: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    mime_code: str = field(
        metadata={
            "name": "mimeCode",
            "type": "Attribute",
            "required": True,
        }
    )
    encoding_code: Optional[str] = field(
        default=None,
        metadata={
            "name": "encodingCode",
            "type": "Attribute",
        },
    )
    uri: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    filename: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class AmountType(BaseModel):
    """<ns1:UniqueID
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000001</ns1:UniqueID>
    <ns1:CategoryCode
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT</ns1:CategoryCode>
    <ns1:DictionaryEntryName
    xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Amount.

    Type</ns1:DictionaryEntryName>
    <ns1:VersionID xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">1.0</ns1:VersionID>
    <ns1:Definition xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">A number of monetary units specified in a currency where the unit of the currency is explicit or
    implied.</ns1:Definition>
    <ns1:RepresentationTermName xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Amount</ns1:RepresentationTermName>
    <ns1:PrimitiveType xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">decimal</ns1:PrimitiveType>

    :ivar value:
    :ivar currency_id: <ns1:UniqueID
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">UDT000001-SC2</ns1:UniqueID>
        <ns1:CategoryCode
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">SC</ns1:CategoryCode>
        <ns1:DictionaryEntryName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Amount
        Currency. Identifier</ns1:DictionaryEntryName> <ns1:Definition
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">The currency
        of the amount.</ns1:Definition> <ns1:ObjectClass
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Amount
        Currency</ns1:ObjectClass> <ns1:PropertyTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identification</ns1:PropertyTermName>
        <ns1:RepresentationTermName
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">Identifier</ns1:RepresentationTermName>
        <ns1:PrimitiveType
        xmlns:ns1="urn:un:unece:uncefact:documentation:1.1">string</ns1:PrimitiveType>
    """

    model_config = ConfigDict(defer_build=True)
    value: Decimal = field(
        metadata={
            "required": True,
        }
    )
    currency_id: Union[CurrencyCodeContentType, str] = field(
        metadata={
            "name": "currencyID",
            "type": "Attribute",
            "required": True,
        }
    )
