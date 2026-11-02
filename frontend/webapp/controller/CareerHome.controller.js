
sap.ui.define([
    "sap/ui/core/mvc/Controller",
    "sap/m/MessageToast",
    "sap/m/MessageBox",
    "sap/ui/model/json/JSONModel"
], function (Controller, MessageToast, MessageBox, JSONModel) {
    "use strict";

    return Controller.extend(
        "com.careerorchestrator.careerorchestrator.controller.CareerHome",
        {

            // INITIALIZE USER MODEL
            onInit: function () {
                var oUserModel = new JSONModel({
                    name: "Your Name"
                });

                this.getView().setModel(oUserModel, "user");
            },

            // SWITCH TO SIGN-UP
            onShowSignup: function () {
                this.byId("loginSection").setVisible(false);
                this.byId("signupSection").setVisible(true);

                this.byId("loginTab").removeStyleClass("activeTab");
                this.byId("signupTab").addStyleClass("activeTab");
            },

            // SWITCH TO LOGIN
            onShowLogin: function () {
                this.byId("signupSection").setVisible(false);
                this.byId("loginSection").setVisible(true);

                this.byId("signupTab").removeStyleClass("activeTab");
                this.byId("loginTab").addStyleClass("activeTab");
            },

            // LOGIN VALIDATION
            onSignIn: function () {
                var email = this.byId("emailInput").getValue().trim();
                var password = this.byId("passwordInput").getValue();

                if (!email || !password) {
                    MessageBox.warning("Please enter your email and password.");
                    return;
                }

                MessageToast.show(
                    "Login form validated. Backend authentication is not connected yet."
                );
            },

            // SIGN-UP VALIDATION
            onSignUp: function () {
                var name = this.byId("nameInput").getValue().trim();
                var email = this.byId("signupEmailInput").getValue().trim();
                var password = this.byId("signupPasswordInput").getValue();
                var confirmPassword = this.byId("confirmPasswordInput").getValue();

                if (!name || !email || !password || !confirmPassword) {
                    MessageBox.warning("Please fill in all fields.");
                    return;
                }

                if (password.length < 8) {
                    MessageBox.warning("Password must contain at least 8 characters.");
                    return;
                }

                if (password !== confirmPassword) {
                    MessageBox.error("Passwords do not match.");
                    return;
                }

                MessageToast.show(
                    "Sign-up form validated. Backend registration is not connected yet."
                );
            },

            // UPDATE USER NAME AFTER SUCCESSFUL BACKEND LOGIN
            onLoginSuccess: function (oUserData) {
                if (!oUserData || !oUserData.name) {
                    MessageBox.error("User information was not received.");
                    return;
                }

                this.getView()
                    .getModel("user")
                    .setProperty("/name", oUserData.name);

                MessageToast.show("Welcome back, " + oUserData.name + "!");
            }

        }
    );
});
