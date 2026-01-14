/**
 * @typedef QueryParams
 * @type {object}
 * @property {string} state
 * @property {string?} code
 * @property {string?} error
 * @property {string?} error_description
 *
 * @typedef Properties
 * @type {object}
 * @property {QueryParams} query_params
 */
import van from '../../../van.min.js';
import { Streamlit } from '../../../streamlit.js';
import { emitEvent, getValue, loadStylesheet, resizeFrameHeightOnDOMChange, resizeFrameHeightToElement } from '../../../utils.js';
import { Card } from '../../../components/card.js';
import { Button } from '../../../components/button.js';
import { Icon } from '../../../components/icon.js';
import { Attribute } from '../../../components/attribute.js';

const { div, span } = van.tags;

const SSOLogin = (/** @type Properties */ props) => {
    loadStylesheet('ssoLogin', stylesheet);
    window.testgen.isPage = true;
    Streamlit.setFrameHeight(1);

    const wrapperId = 'tg-sso-wrapper';
    resizeFrameHeightToElement(wrapperId);
    resizeFrameHeightOnDOMChange(wrapperId);

    // Streamlit's st.login does not expose OpenID auth errors
    // https://github.com/streamlit/streamlit/issues/10160
    // It just redirects to our login page, which in turn redirects back to auth provider, causing an infinite loop

    // To work around this, we configure the redirect URL to be our '/' login path (instead of Streamlit's '/oauth2callback' path)
    // This has to be set in .streamlit/secrets.toml > [auth] > redirect_uri and also in the auth provider's allowed callback URLs

    // Our login page then does the following:
    // - If auth provider returned error in query params, surface details to user
    // - If auth provider returned code in query params, redirect to Streamlit's '/oauth2callback' path to complete auth flow
    // - If no query params, redirect to auth provider to start auth flow

    const queryParams = getValue(props.query_params);

    return div(
        { id: wrapperId, class: 'tg-sso-wrapper' },
        queryParams.error
            ? AuthError(queryParams)
            : (queryParams.code
                ? AuthCallback(queryParams)
                : AuthStart()
            ),
    );
}

const AuthError = (/** @type QueryParams */ queryParams) => {
    let errorDetails = queryParams.error_description;
    try {
        const detailsObject = JSON.parse(errorDetails);
        errorDetails = Object.entries(detailsObject).map(([key, value]) => `${key}: ${value}`).join('\n');
    } catch {}

    return Card({
        border: true,
        title: div(
            { class: 'flex-row fx-gap-2 text-error' },
            Icon({ classes: 'text-error' }, 'warning'),
            span({ style: 'text-transform: none;' }, 'Something went wrong'),
        ),
        content: div(
            { class: 'flex-column fx-gap-5 mt-4' },
            Attribute({ label: 'Error', value: queryParams.error }),
            Attribute({ label: 'Details', value: errorDetails, class: 'tg-sso-error-details' }),
            Button({
                type: 'stroked',
                color: 'primary',
                label: 'Try Again',
                icon: 'arrow_forward',
                width: 200,
                style: 'align-self: flex-end; margin-top: 16px;',
                onclick: () => emitEvent('LoginRedirect'),
            }),
        )
    });
};

const AuthCallback = (/** @type QueryParams */ queryParams) => {
    const url = new URL('oauth2callback', window.top.location.origin);
    Object.entries(queryParams).forEach(([key, value]) => {
        url.searchParams.append(key, value);
    });
    window.top.testgen.changeLocation(url);

    return div(
        { class: 'tg-sso-message' },
        'Logging in ...',
    );
};

const AuthStart = () => {
    emitEvent('LoginRedirect');
    return div(
        { class: 'tg-sso-message' },
        'Redirecting to authentication provider ...',
    );
};

const stylesheet = new CSSStyleSheet();
stylesheet.replace(`
.tg-sso-wrapper {
    padding-top: 100px;
}

.tg-sso-error-details {
    white-space: pre-wrap;
    line-height: 22px;
}

.tg-sso-message {
    font-size: 20px;
    text-align: center;
}
`);

export { SSOLogin };
