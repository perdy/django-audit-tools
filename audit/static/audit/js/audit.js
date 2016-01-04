AuditTools = typeof AuditTools != 'undefined' ? AuditTools : {};
(function(){
    AuditTools.Audit = {};

    AuditTools.Audit.ShowLoadScreen = function() {
        $('#loadScreen').css('visibility', 'visible');
    };

    AuditTools.Audit.HideLoadScreen = function () {
        $('#loadScreen').css('visibility', 'hidden');
    };
})();