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

