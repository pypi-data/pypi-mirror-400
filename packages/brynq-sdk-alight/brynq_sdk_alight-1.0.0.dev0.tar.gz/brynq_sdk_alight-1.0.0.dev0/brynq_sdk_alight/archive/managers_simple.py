"""
Simplified manager for the Alight SDK.
Pure dictionary transformations - no unnecessary classes or complexity.
"""

from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from . import Alight


class EmployeeManager:
    """Simple employee manager - just flat-to-nested dictionary conversion."""

    def __init__(self, alight_sdk: 'Alight'):
        self.alight_sdk = alight_sdk

        # Simple field categorization
        self.field_categories = {
            'extension': ['iban', 'bic', 'account_holder', 'notes'],
            'salary': ['base_salary', 'bonus_amount', 'salary_currency', 'pay_element_code'],
            'job': ['job_title', 'weekly_hours', 'country'],
        }

    def create_newhire_simple(self, flat_data: Dict[str, Any],
                             logical_id: Optional[str] = None,
                             pretty_print: bool = True,
                             save_to_file: bool = False,
                             filename: Optional[str] = None) -> str:
        """
        Create NewHire XML from flat dictionary - that's it!

        Args:
            flat_data: Simple flat dictionary with snake_case keys
            logical_id: Optional logical ID
            pretty_print: Format XML nicely
            save_to_file: Save to file
            filename: Optional filename

        Returns:
            str: HR-XML ready for Alight
        """
        nested_data = self._flat_to_nested(flat_data)
        return self.alight_sdk.generate_newhire_xml(
            person_data=nested_data.get('person_data'),
            extension_data=nested_data.get('extension_data'),
            pay_elements_data=nested_data.get('salary_data'),
            logical_id=logical_id,
            pretty_print=pretty_print
        )

    def create_employee_change_simple(self, flat_data: Dict[str, Any],
                                     logical_id: Optional[str] = None,
                                     pretty_print: bool = True,
                                     save_to_file: bool = False,
                                     filename: Optional[str] = None) -> str:
        """
        Create Employee Change XML from flat dictionary - that's it!
        """
        nested_data = self._flat_to_nested(flat_data)
        return self.alight_sdk.generate_employee_change_xml(
            person_data=nested_data.get('person_data'),
            extension_data=nested_data.get('extension_data'),
            pay_elements_data=nested_data.get('salary_data'),
            logical_id=logical_id,
            pretty_print=pretty_print
        )

    def _flat_to_nested(self, flat_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert flat data to nested - the ONLY transformation we need."""
        result = {}

        # Categorize fields
        person_fields = {}
        extension_fields = {}
        salary_fields = {}
        job_fields = {}

        for key, value in flat_data.items():
            if key in self.field_categories['extension']:
                extension_fields[key] = value
            elif key in self.field_categories['salary']:
                salary_fields[key] = value
            elif key in self.field_categories['job']:
                job_fields[key] = value
            else:
                person_fields[key] = value

        # Build structures (simple dictionary operations)
        if person_fields:
            result['person_data'] = self._build_person_data(person_fields)

        if extension_fields:
            result['extension_data'] = self._build_extension_data(extension_fields)

        if salary_fields:
            result['salary_data'] = self._build_salary_data(salary_fields)

        if job_fields:
            # Add job data to person_data (deployment section)
            if 'person_data' not in result:
                result['person_data'] = {}
            result['person_data']['deployment'] = self._build_job_data(job_fields, flat_data)

        return result

    def _build_person_data(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Build person data structure with automatic {"value": ...} wrapping."""
        person_data = {}
        person_section = {}
        employment_section = {}

        # Person identification
        if fields.get('person_id'):
            person_section['person_id'] = [{"value": fields['person_id']}]

        # Names
        if fields.get('first_name') or fields.get('last_name'):
            person_section['person_name'] = [{}]
            if fields.get('first_name'):
                person_section['person_name'][0]['given_name'] = [{"value": fields['first_name']}]
            if fields.get('last_name'):
                person_section['person_name'][0]['family_name'] = [{"value": fields['last_name']}]

        # Birth date
        if fields.get('birth_date'):
            person_section['birth_date'] = {"value": fields['birth_date']}

        # Contact info
        if fields.get('email'):
            person_section['communication'] = person_section.get('communication', [])
            person_section['communication'].append({
                "type": "Email",
                "uri": {"value": fields['email']}
            })

        if fields.get('phone'):
            person_section['communication'] = person_section.get('communication', [])
            person_section['communication'].append({
                "type": "Phone",
                "dial_number": {"value": fields['phone']}
            })

        # Employment dates
        hire_date = fields.get('hire_date')
        effective_date = fields.get('effective_date')
        actual_date = hire_date or effective_date

        if actual_date:
            employment_section['employment_lifecycle'] = [{
                "valid_from": actual_date,
                "hire": {
                    "hire_date": {"value": actual_date},
                    "original_hire_date": {"value": actual_date}
                }
            }]

        if fields.get('employee_id'):
            employment_section['employee_id'] = [{"value": fields['employee_id']}]

        # Assemble
        if person_section:
            person_data['person'] = person_section
        if employment_section:
            person_data['employment'] = employment_section

        return person_data

    def _build_extension_data(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Build extension data (payment info, etc.)."""
        extension_data = {}

        # Payment instruction
        if any(fields.get(k) for k in ['iban', 'bic', 'account_holder']):
            extension_data['payment_instruction'] = {}
            if fields.get('iban'):
                extension_data['payment_instruction']['iban'] = fields['iban']
            if fields.get('bic'):
                extension_data['payment_instruction']['bic'] = fields['bic']
            if fields.get('account_holder'):
                extension_data['payment_instruction']['holder_name'] = fields['account_holder']

        if fields.get('notes'):
            extension_data['note'] = fields['notes']

        return extension_data

    def _build_salary_data(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Build salary data."""
        salary_data = {}
        pay_elements = []

        if fields.get('base_salary'):
            pay_elements.append({
                "code": "BASE",
                "amount": fields['base_salary'],
                "valid_from": fields.get('effective_date') or fields.get('hire_date')
            })

        if fields.get('bonus_amount'):
            pay_elements.append({
                "code": "BONUS",
                "amount": fields['bonus_amount'],
                "valid_from": fields.get('effective_date') or fields.get('hire_date')
            })

        if pay_elements:
            salary_data['pay_element'] = pay_elements

        return salary_data

    def _build_job_data(self, job_fields: Dict[str, Any], all_fields: Dict[str, Any]) -> Dict[str, Any]:
        """Build job/deployment data."""
        job_data = {}

        actual_date = all_fields.get('hire_date') or all_fields.get('effective_date')
        if actual_date:
            job_data['valid_from'] = actual_date

        if job_fields.get('job_title'):
            job_data['job'] = {"title": job_fields['job_title']}

        if job_fields.get('weekly_hours'):
            job_data['schedule'] = {"weekly_hours": job_fields['weekly_hours']}

        if job_fields.get('country'):
            job_data['work_location'] = {"country": job_fields['country']}

        return job_data
