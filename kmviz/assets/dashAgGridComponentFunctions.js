var dagcomponentfuncs = window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {};

dagcomponentfuncs.CustomLoadingOverlay = function (props) {
    return React.createElement(
        'div',
        {
            style: {
                border: '1pt dotted grey',
                borderRadius: '30px',
                color: props.color || 'grey',
                padding: 10,
            },
        },
        props.loadingMessage
    );
};

dagcomponentfuncs.RenderLink = function (props) {
    return React.createElement(
        'a',
        {href: props.link_prefix + props.value + props.link_suffix, target: props.link_target},
        props.value
    );
};