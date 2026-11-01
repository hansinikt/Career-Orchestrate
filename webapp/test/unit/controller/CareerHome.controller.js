/*global QUnit*/

sap.ui.define([
	"com/careerorchestrator/careerorchestrator/controller/CareerHome.controller"
], function (Controller) {
	"use strict";

	QUnit.module("CareerHome Controller");

	QUnit.test("I should test the CareerHome controller", function (assert) {
		var oAppController = new Controller();
		oAppController.onInit();
		assert.ok(oAppController);
	});

});
