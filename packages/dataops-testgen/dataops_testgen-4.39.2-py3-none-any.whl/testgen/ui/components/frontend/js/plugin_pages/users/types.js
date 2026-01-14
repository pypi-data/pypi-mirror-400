/**
 * @typedef {'admin' | 'data_quality' | 'analyst' | 'business' | 'catalog'} Role
 *
 * @typedef User
 * @type {object}
 * @property {string} id
 * @property {string} username
 * @property {string?} name
 * @property {string?} email
 * @property {string?} password
 * @property {Role} role
 * @property {number?} latest_login
 */

export const ROLE_OPTIONS = [
    { value: 'admin', label: 'Admin', help: 'Full access to all features.' },
    { value: 'data_quality', label: 'Data Quality', help: 'Can manage table groups and test suites, run profiling and tests, disposition results, and edit Data Catalog tags. \nRead-only access to Connections and Projects Settings.' },
    { value: 'analyst', label: 'Analyst', help: 'Can disposition results and edit Data Catalog tags. \nRead-only access to all other features.' },
    { value: 'business', label: 'Business', help: 'Read-only access to all features.' },
    { value: 'catalog', label: 'Catalog', help: 'Read-only access to Data Catalog only.' },
];
