/**
 * @fileoverview Dropdown options and field definitions for the ClientIntake form.
 */

export const INDUSTRY_OPTIONS = [
  { value: 'salons_spas',      label: 'Salons & Spas' },
  { value: 'legal',            label: 'Legal & Professional Services' },
  { value: 'home_services',    label: 'Home Services' },
  { value: 'medical_dental',   label: 'Medical & Dental' },
  { value: 'restaurant',       label: 'Restaurant & Hospitality' },
  { value: 'retail',           label: 'Retail' },
  { value: 'fitness_wellness', label: 'Fitness & Wellness' },
  { value: 'other',            label: 'Other' },
];

export const GBP_ACCESS_OPTIONS = [
  { value: 'full_access',     label: 'Full Access' },
  { value: 'pending',         label: 'Pending Access' },
  { value: 'no_access',       label: 'No Access Yet' },
  { value: 'needs_claiming',  label: 'Needs Claiming' },
  { value: 'doesnt_exist',    label: 'Profile Does Not Exist' },
];

export const START_TYPE_OPTIONS = [
  { value: 'new',         label: 'Brand New — No Online Presence' },
  { value: 'minimal',     label: 'Minimal — Basic Listing, Few Reviews' },
  { value: 'established', label: 'Established — Active Profile, Some Reviews' },
  { value: 'strong',      label: 'Strong — Solid Profile, Needs Optimisation' },
];
