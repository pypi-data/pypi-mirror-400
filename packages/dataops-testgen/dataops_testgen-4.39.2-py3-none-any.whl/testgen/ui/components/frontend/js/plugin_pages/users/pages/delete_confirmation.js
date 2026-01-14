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
 * @property {Result?} result
 */

import van from '../../../van.min.js';
import { Streamlit } from '../../../streamlit.js';
import { emitEvent, getValue, resizeFrameHeightOnDOMChange, resizeFrameHeightToElement } from '../../../utils.js';
import { Button } from '../../../components/button.js';
import { Alert } from '../../../components/alert.js';

const { div, span, b } = van.tags;

/**
 * @param {Properties} props
 * @returns
 */
const UserDeleteConfirmation = (props) => {
    Streamlit.setFrameHeight(1);
    window.testgen.isPage = true;

    const domId = 'user-delete-confirmation';
    resizeFrameHeightToElement(domId);
    resizeFrameHeightOnDOMChange(domId);

    const user = getValue(props.user);

    return div(
        { id: domId, class: 'flex-column' },
        div(
            { class: 'flex-column fx-gap-4' },
            span(
                'Are you sure you want to delete the user ',
                b(user.username),
                '?',
            ),
        ),
        div(
            { class: 'flex-row fx-justify-content-flex-end' },
            Button({
                type: 'flat',
                color: 'warn',
                label: 'Delete',
                style: 'width: auto;',
                onclick: () => emitEvent('DeleteUserConfirmed'),
            }),
        ),
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

export { UserDeleteConfirmation };
