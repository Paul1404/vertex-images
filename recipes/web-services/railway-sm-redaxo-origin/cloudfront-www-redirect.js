function handler(event) {
    var request = event.request;
    var host = request.headers.host && request.headers.host.value;

    if (host && host.toLowerCase() === 'www.schlossmuehle-untereuerheim.de') {
        var query = request.rawQueryString();
        if (!query) {
            var parameters = [];
            for (var key in request.querystring) {
                if (!Object.prototype.hasOwnProperty.call(request.querystring, key)) {
                    continue;
                }
                var parameter = request.querystring[key];
                if (parameter.multiValue) {
                    for (var i = 0; i < parameter.multiValue.length; i++) {
                        parameters.push(key + '=' + parameter.multiValue[i].value);
                    }
                } else {
                    parameters.push(key + '=' + parameter.value);
                }
            }
            query = parameters.join('&');
        }
        return {
            statusCode: 308,
            statusDescription: 'Permanent Redirect',
            headers: {
                location: {
                    value: 'https://schlossmuehle-untereuerheim.de' +
                        request.uri + (query ? '?' + query : '')
                }
            }
        };
    }

    return request;
}
