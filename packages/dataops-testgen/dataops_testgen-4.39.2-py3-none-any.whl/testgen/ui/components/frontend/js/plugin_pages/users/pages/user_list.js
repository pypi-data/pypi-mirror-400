/**
 * @import { User } from '../types.js';
 *
 * @typedef Properties
 * @type {object}
 * @property {User[]} users
 * @property {string} current_username
 * @property {boolean} use_sso_auth
 */
import van from '../../../van.min.js';
import { Streamlit } from '../../../streamlit.js';
import { Button } from '../../../components/button.js';
import { Select } from '../../../components/select.js';
import { Input } from '../../../components/input.js';
import { getValue, emitEvent, loadStylesheet, resizeFrameHeightToElement, resizeFrameHeightOnDOMChange } from '../../../utils.js';
import { formatTimestamp } from '../../../display_utils.js';
import { ROLE_OPTIONS } from '../types.js';

const { div, span } = van.tags;

/**
 * @param {Properties} props
 * @returns {HTMLElement}
 */
const UserList = (props) => {
    loadStylesheet('userList', stylesheet);
    Streamlit.setFrameHeight(1);
    window.testgen.isPage = true;

    const domId = 'users-page';
    resizeFrameHeightToElement(domId);
    resizeFrameHeightOnDOMChange(domId);

    const currentUsername = getValue(props.current_username);
    const useSSOAuth = getValue(props.use_sso_auth);

    const displayColumns = ['username', 'name_email', 'role', 'latest_login', 'actions'];
    let columnSizes = COLUMN_SIZES;
    if (useSSOAuth) {
        displayColumns.shift();
        columnSizes = SSO_COLUMN_SIZES;
    }

    return div(
        { id: domId, class: 'tg-users' },
        Toolbar(useSSOAuth),
        () => getValue(props.users)?.length
            ? div(
                { class: 'table tg-users-table' },
                div(
                    { class: 'table-header flex-row' },
                    displayColumns.map(column => span(
                        {
                            style: `flex: 0 0 ${columnSizes[column]}`,
                            class: column,
                        },
                        COLUMN_LABELS[column],
                    )),
                ),
                () => div(
                    getValue(props.users)?.map(user => div(
                        { class: 'table-row flex-row' },
                        displayColumns.map(column => div(
                            {
                                style: `flex: 0 0 ${columnSizes[column]}; max-width: ${columnSizes[column]};`,
                                class: column,
                            },
                            TableCell(user, column, user.username === currentUsername, useSSOAuth),
                        )),
                    )),
                ),
            )
            : div(
                { class: 'pt-7 text-secondary', style: 'text-align: center;' },
                'No users found matching filters',
            ),
    );
}

const Toolbar = (
    /** @type boolean */ useSSOAuth,
    /** @type Role? */ selectedRole,
    /** @type string? */ searchFilter,
) => {
    const role = van.state(selectedRole || null);
    const search = van.state(searchFilter || null);

    van.derive(() => {
        if (role.val !== selectedRole || search.val !== searchFilter) {
            emitEvent('UsersFiltered', { payload: { role: role.val || null, search: search.val || null } });
        }
    });

    return div(
        { class: 'flex-row fx-align-flex-end fx-gap-4 fx-justify-space-between fx-flex-wrap mb-4' },
        div(
            { class: 'flex-row fx-align-flex-end fx-gap-4' },
            Select({
                label: 'Role',
                allowNull: true,
                value: selectedRole,
                options: ROLE_OPTIONS,
                onChange: (value) => role.val = value,
            }),
            Input({
                icon: 'search',
                label: '',
                placeholder: 'Search users',
                width: 300,
                clearable: true,
                value: searchFilter,
                onChange: (value) => search.val = value || null,
            }),
        ),
        !useSSOAuth
            ? Button({
                type: 'stroked',
                icon: 'add',
                label: 'Add User',
                color: 'basic',
                style: 'background: var(--button-generic-background-color); width: unset;',
                onclick: () => emitEvent('AddUserClicked', {}),
            })
            : null,
    );
}

const TableCell = (
    /** @type User */ user,
    /** @type string */ column,
    /** @type boolean */ isCurrentUser,
    /** @type boolean */ useSSOAuth,
) => {
    const componentByColumn = {
        username: UsernameCell,
        name_email: NameEmailCell,
        role: RoleCell,
        latest_login: LatestLoginCell,
        actions: ActionsCell,
    };

    if (componentByColumn[column]) {
        return componentByColumn[column](user, isCurrentUser, useSSOAuth);
    }
    return span({ style: 'word-wrap: break-word;' }, user[column] || '--');
};

const UsernameCell = (/** @type User */ user, /** @type boolean */ isCurrentUser, /** @type boolean */ useSSOAuth) => {
    return span(
        { class: isCurrentUser ? 'text-green' : '', style: 'word-wrap: break-word;' },
        user.username,
    );
};

const NameEmailCell = (/** @type User */ user, /** @type boolean */ isCurrentUser, /** @type boolean */ useSSOAuth) => {
    return div(
        { class: 'flex-column fx-gap-1' },
        span({ class: isCurrentUser ? 'text-green' : '' }, user.name || '--'),
        user.email !== user.name
            ? span({ class: 'text-caption' }, user.email)
            : null,
    );
};

const RoleCell = (/** @type User */ user, /** @type boolean */ isCurrentUser, /** @type boolean */ useSSOAuth) => {
    return span(
        { style: 'text-transform: capitalize;' },
        user.role.replace('_', ' '),
    );
};

const LatestLoginCell = (/** @type User */ user, /** @type boolean */ isCurrentUser, /** @type boolean */ useSSOAuth) => {
    return span(formatTimestamp(user.latest_login));
};

const ActionsCell = (/** @type User */ user, /** @type boolean */ isCurrentUser, /** @type boolean */ useSSOAuth) => {
    return div(
        { class: 'flex-row fx-justify-content-flex-end' },
        Button({
            type: 'icon',
            icon: 'edit',
            disabled: isCurrentUser && useSSOAuth,
            onclick: () => emitEvent('EditUserClicked', { payload: user.username }),
        }),
        Button({
            type: 'icon',
            icon: 'delete',
            disabled: isCurrentUser,
            onclick: () => emitEvent('DeleteUserClicked', { payload: user.username }),
        }),
    );
};

const COLUMN_LABELS = {
    username: 'Username',
    name_email: 'Name | Email',
    role: 'Role',
    latest_login: 'Latest Login',
    actions: 'Actions',
};

const COLUMN_SIZES = {
    username: '30%',
    name_email: '30%',
    role: '15%',
    latest_login: '15%',
    actions: '10%',
};

const SSO_COLUMN_SIZES = {
    name_email: '40%',
    role: '25%',
    latest_login: '25%',
    actions: '10%',
};

const stylesheet = new CSSStyleSheet();
stylesheet.replace(`
.tg-users {
    min-height: 400px;
}

.table-header > .actions,
.table-row > .actions {
    text-align: right;
    min-width: 80px;
}
`);

export { UserList };
