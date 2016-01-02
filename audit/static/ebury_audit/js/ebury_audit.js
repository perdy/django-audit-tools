AuditTools = typeof AuditTools != 'undefined' ? AuditTools : {};
(function(){
    AuditTools.Audit = {};
    AuditTools.Audit.LoadScreen = {};

    AuditTools.Audit.LoadScreen.ShowLoadScreen = function() {
        $('#loadScreen').css('visibility', 'visible');
    };

    AuditTools.Audit.LoadScreen.HideLoadScreen = function () {
        $('#loadScreen').css('visibility', 'hidden');
    };
})();