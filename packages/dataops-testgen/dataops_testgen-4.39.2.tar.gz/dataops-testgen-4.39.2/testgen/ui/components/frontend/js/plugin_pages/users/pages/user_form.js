/**
 * @import { User } from '../types.js';
 *
 * @typedef Result
 * @type {object}
 * @property {boolean} success
 * @property {string} message
 *
 * @typedef Properties
 * @type {object}
 * @property {User} user
 * @property {boolean} use_sso_auth
 * @property {Result?} result
 */
import van from '../../../van.min.js';
import { Streamlit } from '../../../streamlit.js';
import { Button } from '../../../components/button.js';
import { Attribute } from '../../../components/attribute.js';
import { Input } from '../../../components/input.js';
import { emitEvent, getValue, isEqual, resizeFrameHeightOnDOMChange, resizeFrameHeightToElement } from '../../../utils.js';
import { minLength, noSpaces, required } from '../../../form_validators.js';
import { RadioGroup } from '../../../components/radio_group.js';
import { Alert } from '../../../components/alert.js';
import { ROLE_OPTIONS } from '../types.js';

const { div } = van.tags;
const minUsernameLength = 3;
const minPasswordLength = 8;
const secretsPlaceholder = '<hidden for safety reasons>';

/**
 *
 * @param {Properties} props
 * @returns
 */
const UserForm = (props) => {
    Streamlit.setFrameHeight(1);
    window.testgen.isPage = true;

    const domId = 'user-form';
    resizeFrameHeightToElement(domId);
    resizeFrameHeightOnDOMChange(domId);

    const user = getValue(props.user);
    const useSSOAuth = getValue(props.use_sso_auth);

    const updatedUser = van.state(user);
    const validityPerField = van.state({});

    const onFieldChange = (field, value, validity) => {
        updatedUser.val = { ...updatedUser.rawVal, [field]: value };
        validityPerField.val = { ...validityPerField.rawVal, [field]: validity };
    };

    return div(
        { id: domId },
        useSSOAuth
            ? SSOAttributes(user)
            : NativeForm(user, onFieldChange),
        div(
            { class: 'mt-4 mb-4' },
            RadioGroup({
                label: 'Role',
                options: ROLE_OPTIONS,
                layout: 'vertical',
                value: user?.role,
                onChange: (value) => onFieldChange('role', value, true),
            }),
        ),
        () => {
            const formValid = Object.keys(validityPerField.val).length > 0 && Object.values(validityPerField.val).every(v => v);
            const formDirty = !isEqual(updatedUser.val, user);

            return Button({
                label: user?.id ? 'Save' : 'Add',
                color: 'primary',
                type: 'flat',
                width: 'auto',
                style: 'margin-left: auto;',
                disabled: !(formDirty && formValid),
                onclick: () => emitEvent('SaveUserClicked', { payload: updatedUser.val }),
            });
        },
        () => {
            const result = getValue(props.result);
            return result
                ? Alert(
                    { type: result.success ? 'success' : 'error', class: 'mt-3' },
                    div(result.message),
                )
                : '';
        },
    );
};

const NativeForm = (/** @type User? */ user, /** @type Function */ onFieldChange) => {
    const inputHeight = 38;
    const passwordValidators = [ noSpaces, minLength(minPasswordLength) ];
    if (!user?.id) {
        passwordValidators.unshift(required);
    }

    return div(
        { class: 'flex-column fx-gap-3' },
        Input({
            name: 'username',
            label: 'Username',
            value: user?.username,
            height: inputHeight,
            onChange: (value, state) => onFieldChange('username', value, state.valid),
            validators: [ required, noSpaces, minLength(minUsernameLength) ],
        }),
        Input({
            name: 'password',
            label: 'Password',
            type: 'password',
            height: inputHeight,
            placeholder: user?.id && user.password ? secretsPlaceholder : '',
            onChange: (value, state) => onFieldChange('password', value || user?.password, state.valid),
            validators: passwordValidators,
        }),
        Input({
            name: 'name',
            label: 'Name',
            value: user?.name,
            height: inputHeight,
            onChange: (value, state) => onFieldChange('name', value, state.valid),
        }),
        Input({
            name: 'email',
            label: 'Email',
            value: user?.email,
            height: inputHeight,
            onChange: (value, state) => onFieldChange('email', value, state.valid),
        }),
    )
};

const SSOAttributes = (/** @type User? */ user) => {
    return div(
        { class: 'flex-column fx-gap-4' },
        Attribute({
            label: 'Name',
            value: user?.name,
        }),
        Attribute({
            label: 'Email',
            value: user?.email,
        }),
    );
};

export { UserForm };
